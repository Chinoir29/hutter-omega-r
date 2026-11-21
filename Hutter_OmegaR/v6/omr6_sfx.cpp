// OMÉGA-R v0.6: parameter sweep of the causal context/match table capacity.
// Baseline behavior is identical to v0.5 for TBITS=15 MATCH_BITS=18 RING_BITS=20.
// EXPERIMENTAL: No verified enwik9 score.
// Copyright 2026 OMÉGA-R Research. SPDX-License-Identifier: MIT.
// EXPERIMENTAL: NOT a record competitor, not a validated Hutter submission.
// Usage: ./comp9 [input=enwik9] [output=archive9] [mode=adaptive-match-calib]
// When executed as its own output archive, decodes original bytes into ./data9.
// No external dictionaries, weights, runtime models or auxiliary files.
#define _FILE_OFFSET_BITS 64
#define _POSIX_C_SOURCE 200809L
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <array>
#include <algorithm>
#include <memory>
#include <sys/stat.h>
#include <unistd.h>

namespace omr6 {
#ifndef OMR6_TBITS
#define OMR6_TBITS 15
#endif
#ifndef OMR6_MATCH_BITS
#define OMR6_MATCH_BITS 18
#endif
#ifndef OMR6_RING_BITS
#define OMR6_RING_BITS 20
#endif
constexpr unsigned E=8, ORDER=6, TBITS=OMR6_TBITS;
constexpr unsigned T=1u<<TBITS, T_MASK=T-1;
constexpr unsigned MATCH_BITS=OMR6_MATCH_BITS, MATCH_SIZE=1u<<MATCH_BITS, RING_BITS=OMR6_RING_BITS, RING_SIZE=1u<<RING_BITS;
static_assert(TBITS >= 15 && TBITS <= 20, "Invalid context table size");
static_assert(MATCH_BITS >= 18 && MATCH_BITS <= 22, "Invalid match table size");
static_assert(RING_BITS >= 20 && RING_BITS <= 24, "Invalid ring size");
constexpr uint64_t FNV0=14695981039346656037ull;
constexpr uint64_t FNV_PRIME=1099511628211ull;
constexpr uint32_t HALF=0x80000000u, QTR=0x40000000u, THREEQ=0xc0000000u;
constexpr uint8_t MAGIC[8]={'O','M','R','4','S','F','X','!'};
constexpr size_t FOOTER=32;
struct Cell {uint64_t key; uint16_t c0,c1;};
struct MatchCell {uint64_t key, pos;};
static inline uint64_t mix(uint64_t v) {
  v^=v>>30;v*=0xbf58476d1ce4e5b9ull;
  v^=v>>27;v*=0x94d049bb133111ebull;
  return v^(v>>31);
}
static void store64(uint8_t* p,uint64_t n){for(int i=0;i<8;i++)p[i]=uint8_t(n>>(8*i));}
static uint64_t load64(const uint8_t* p){uint64_t n=0;for(int i=7;i>=0;i--)n=(n<<8)|p[i];return n;}
static bool writeall(FILE* f,const void* buf,size_t n){return !n || fwrite(buf,1,n,f)==n;}
static int err(const char* s){fprintf(stderr,"OMR6: %s\n",s);return 1;}
static int64_t filesize(FILE* f){if(fseeko(f,0,SEEK_END))return -1;return ftello(f);}
struct BitWriter {
  FILE* f;uint8_t b=0;unsigned count=0;bool ok=true;
  explicit BitWriter(FILE* p):f(p){}
  void put(unsigned bit){b=uint8_t((b<<1)|(bit&1u)); if(++count==8){ok=ok&&writeall(f,&b,1);b=0;count=0;}}
  void flush(){if(count){b<<=(8-count);ok=ok&&writeall(f,&b,1);b=0;count=0;}}
};
struct BitReader {
  FILE* f;uint64_t left;uint8_t b=0;unsigned count=0;bool ok=true;
  BitReader(FILE* p,uint64_t n):f(p),left(n){}
  unsigned get(){if(!count){if(left){if(fread(&b,1,1,f)!=1){ok=false;return 0;}left--;count=8;}else{return 0;}}
    unsigned x=(b>>7)&1;b<<=1;count--;return x;
  }
};
struct ArithmeticEncoder {
  uint32_t low=0,high=0xffffffffu;uint64_t pending=0;BitWriter bw;
  explicit ArithmeticEncoder(FILE* p):bw(p){}
  void emit(unsigned b){bw.put(b);while(pending){bw.put(!b);pending--;}}
  void put(unsigned bit,uint32_t p1){
    uint64_t range=(uint64_t)high-low+1;
    uint32_t mid=low+uint32_t((range*(65536u-p1))>>16)-1u;
    if(bit)low=mid+1u;else high=mid;
    for(;;){
      if(high<HALF)emit(0);
      else if(low>=HALF){emit(1);low-=HALF;high-=HALF;}
      else if(low>=QTR && high<THREEQ){pending++;low-=QTR;high-=QTR;}
      else break;
      low<<=1;high=(high<<1)|1u;
    }
  }
  bool close(){pending++;emit(low<QTR?0:1);bw.flush();return bw.ok;}
};
struct ArithmeticDecoder {
  uint32_t low=0,high=0xffffffffu,value=0;BitReader br;
  ArithmeticDecoder(FILE* p,uint64_t n):br(p,n){for(int i=0;i<32;i++)value=(value<<1)|br.get();}
  unsigned get(uint32_t p1){
    uint64_t range=(uint64_t)high-low+1;
    uint32_t mid=low+uint32_t((range*(65536u-p1))>>16)-1u;
    unsigned bit=(value>mid);
    if(bit)low=mid+1u;else high=mid;
    for(;;){
      if(high<HALF){}
      else if(low>=HALF){value-=HALF;low-=HALF;high-=HALF;}
      else if(low>=QTR && high<THREEQ){value-=QTR;low-=QTR;high-=QTR;}
      else break;
      low<<=1;high=(high<<1)|1u;value=(value<<1)|br.get();
    }
    return bit;
  }
};
struct Predictor {
  std::array<std::unique_ptr<Cell[]>,E> tables;
  uint8_t recent[ORDER-1]={};
  uint64_t word=0,prior_word=0;
  unsigned wordlen=0;
  uint8_t prev=0;
  bool tag=false,adapt,word_enabled,text_gate,enable_match;unsigned min_word,match_style=0;
  std::unique_ptr<MatchCell[]> match_table;
  std::unique_ptr<uint8_t[]> match_ring;
  uint64_t streampos=0,rolling8=0,match_continuation=0,match_position=0;
  uint32_t matched_streak=0;bool match_valid=false;uint8_t match_byte=0;
  struct MatchStat { uint32_t good=0, bad=0; };
  MatchStat match_stats[2][7];unsigned match_bin=0, match_text=0;
  static unsigned bin_streak(uint32_t n){
    if(n==0)return 0;
    if(n==1)return 1;
    if(n<4)return 2;
    if(n<8)return 3;
    if(n<16)return 4;
    if(n<32)return 5;
    return 6;
  }
  unsigned match_weight()const {
    if(match_style==0)return std::min(940u,150u+matched_streak*70u);
    if(match_style==2)return std::min(995u,220u+matched_streak*120u);
    static constexpr unsigned PRIOR_GOOD[7]={2,4,8,16,32,64,128};
    static constexpr unsigned PRIOR_BAD [7]={10,8,5,3,2,2,1};
    const MatchStat& st=match_stats[match_text][match_bin];
    uint64_t g=uint64_t(st.good)+PRIOR_GOOD[match_bin];
    uint64_t b=uint64_t(st.bad)+PRIOR_BAD[match_bin];
    return unsigned(std::min<uint64_t>(995,1000*g/(g+b)));
  }
  unsigned current_prefix=1;
  uint8_t ascii_ring[1024]={};unsigned ring_index=0,text_seen=0,ascii_count=0;
  uint16_t gates[3][8][E]{};
  Cell* selected[E]{};
  uint32_t preds[E]{};
  unsigned cls=0, j=0;
  constexpr static uint16_t base[E]={4,4,6,7,9,11,9,7};
  explicit Predictor(bool adaptive,bool enable_word,unsigned min_support,bool gated,bool matched):adapt(adaptive),word_enabled(enable_word),text_gate(gated),enable_match(matched),min_word(min_support){
    for(auto& t:tables)t=std::unique_ptr<Cell[]>(new Cell[T]());
    if(enable_match){match_table.reset(new MatchCell[MATCH_SIZE]());match_ring.reset(new uint8_t[RING_SIZE]());}
    for(auto& group:gates)for(auto& bit:group)for(auto& w:bit)w=256;
  }
  bool word_active()const{return word_enabled && (!text_gate || (text_seen>=256 && ascii_count*100u>=85u*text_seen));}
  void lookup_match(){
    match_valid=false;
    if(!enable_match || streampos<8)return;
    uint64_t cand=0;
    if(match_continuation>=8 && match_continuation<streampos && streampos-match_continuation<RING_SIZE){
      cand=match_continuation;
    }else{
      uint64_t h=mix(rolling8^0xe7037ed1a0b428dbull);
      const MatchCell& m=match_table[h&(MATCH_SIZE-1u)];
      if(m.key!=h||m.pos<8||m.pos>=streampos||streampos-m.pos>=RING_SIZE)return;
      bool same=true;
      for(unsigned i=0;i<8;i++){
        if(match_ring[(streampos-8+i)&(RING_SIZE-1u)]!=match_ring[(m.pos-8+i)&(RING_SIZE-1u)]){same=false;break;}
      }
      if(!same)return;
      cand=m.pos;
    }
    match_position=cand;
    match_byte=match_ring[cand&(RING_SIZE-1u)];
    match_valid=true;
  }
  void prepare(unsigned bitpos,unsigned prefix){
    j=bitpos;current_prefix=prefix;
    if(bitpos==0 && enable_match){
      lookup_match();match_bin=bin_streak(matched_streak);
      match_text=(text_seen>=256 && ascii_count*100u>=85u*text_seen)?1u:0u;
    }
    cls=tag?1:((prev==10 || prev==32 || prev==9)?2:0);
    uint64_t hs[E];
    hs[0]=0x243f6a8885a308d3ull;
    uint64_t s=hs[0];
    for(unsigned k=1;k<ORDER;k++){s=s*1315423911ull+uint64_t(recent[k-1])+17u;hs[k]=mix(s);}
    hs[6]=mix(word ^(uint64_t(wordlen)<<40)^0xa05e46a9ull);
    hs[7]=mix(word ^(prior_word*0x9e3779b97f4a7c15ull)^0xc4901a88ull);
    uint64_t suffix=mix(uint64_t(prefix)*0xd6e8feb86659fd93ull);
    for(unsigned k=0;k<E;k++){
      if(!word_active() && k>=ORDER){selected[k]=nullptr;preds[k]=32768;continue;}
      uint64_t key=mix(hs[k]^suffix^(uint64_t(k+1)*0x9e3779b97f4a7c15ull));
      Cell& c=tables[k][key&T_MASK];
      if(c.key!=key){c.key=key;c.c0=1;c.c1=1;}
      selected[k]=&c;
      preds[k]=uint32_t((uint64_t(c.c1)*65536u)/(c.c0+c.c1));
      preds[k]=std::max(16u,std::min(65520u,preds[k]));
    }
  }
  uint32_t prob()const{
    uint64_t num=0,den=0;
    for(unsigned k=0;k<E;k++){
      if(!word_active() && k>=ORDER)continue;
      unsigned samples=selected[k]->c0+selected[k]->c1-2u;
      if(k>=ORDER && samples<min_word)continue;
      unsigned w=uint32_t(base[k])*uint32_t(2u+std::min(samples,64u))*gates[cls][j][k];
      den+=w;num+=uint64_t(w)*preds[k];
    }
    uint32_t p=uint32_t(num/den);
    if(enable_match && match_valid && ((unsigned(match_byte)>>(8u-j))==(current_prefix&((1u<<j)-1u)))){
      unsigned b=(match_byte>>(7u-j))&1u;
      unsigned w=match_weight();
      unsigned q=b?65500u:36u;
      p=uint32_t((uint64_t(p)*(1000u-w)+uint64_t(q)*w)/1000u);
    }
    return std::max(128u,std::min(65408u,p));
  }
  void observe(unsigned actual,uint32_t mixp){
    if(adapt){
      int64_t target=actual?65536:0;
      int64_t delta=target-int64_t(mixp);
      for(unsigned k=0;k<E;k++){
        if(!word_active() && k>=ORDER)continue;
        if(k>=ORDER && selected[k]->c0+selected[k]->c1-2u<min_word)continue;
        int64_t change=(delta*(int64_t(preds[k])-int64_t(mixp)))>>29;
        int64_t next=int64_t(gates[cls][j][k])+change;
        gates[cls][j][k]=uint16_t(std::max<int64_t>(64,std::min<int64_t>(1024,next)));
      }
    }
    for(unsigned k=0;k<E;k++){
      if(!word_active() && k>=ORDER)continue;
      Cell* c=selected[k];
      if(actual)c->c1++;else c->c0++;
      if(c->c0+c->c1>2048){c->c0=uint16_t((c->c0+1)/2);c->c1=uint16_t((c->c1+1)/2);}
    }
  }
  static bool wordchar(uint8_t c){return (c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='_';}
  void advance(uint8_t c){
    if(enable_match){
      if(match_valid && match_style==1){
        MatchStat& st=match_stats[match_text][match_bin];
        if(c==match_byte)st.good++;else st.bad++;
        if(st.good+st.bad>8192){st.good=(st.good+1)/2;st.bad=(st.bad+1)/2;}
      }
      if(match_valid && c==match_byte){
        match_continuation=match_position+1;
        matched_streak=std::min(64u,matched_streak+1);
      }else{match_continuation=0;matched_streak=0;}
      if(streampos>=8){
        uint64_t h=mix(rolling8^0xe7037ed1a0b428dbull);
        match_table[h&(MATCH_SIZE-1u)]={h,streampos};
      }
      match_ring[streampos&(RING_SIZE-1u)]=c;
      rolling8=(rolling8<<8)|c;
      streampos++;
    }
    unsigned ascii = (c>=32&&c<=126)||c==9||c==10||c==13;
    if(text_seen==1024)ascii_count-=ascii_ring[ring_index];else text_seen++;
    ascii_count+=ascii;ascii_ring[ring_index]=uint8_t(ascii);ring_index=(ring_index+1)%1024;
    if(wordchar(c)){
      if(wordlen<255)wordlen++;
      word=word*1315423911ull+uint64_t(c)+1;
    }else{
      if(wordlen){prior_word=word;word=0;wordlen=0;}
    }
    if(c=='<')tag=true;
    if(c=='>')tag=false;
    for(unsigned k=ORDER-2;k>0;k--)recent[k]=recent[k-1];
    recent[0]=c;prev=c;
  }
};
constexpr uint16_t Predictor::base[E];
static bool copy_self(FILE* self,FILE* out,uint64_t n){
  uint8_t buffer[1<<16];if(fseeko(self,0,SEEK_SET))return false;
  while(n){size_t size=size_t(std::min<uint64_t>(n,sizeof(buffer)));
    if(fread(buffer,1,size,self)!=size || !writeall(out,buffer,size))return false;
    n-=size;
  }return true;
}
static int encode(FILE* self,const char* path,const char* dst,bool adaptive,bool enable_word,unsigned min_support,bool text_gate,bool enable_match,unsigned match_style){
  if(!strcmp(path,dst))return err("Refuse to overwrite input");
  FILE* in=fopen(path,"rb");if(!in)return err("Input file unavailable");
  FILE* out=fopen(dst,"wb");if(!out){fclose(in);return err("Output unavailable");}
  int status=1;
  int64_t sz=filesize(self);
  if(sz<0 || !copy_self(self,out,uint64_t(sz)))goto finish;
  {
    std::unique_ptr<Predictor> p(new Predictor(adaptive,enable_word,min_support,text_gate,enable_match));
    p->match_style=match_style;
    ArithmeticEncoder coder(out);
    uint8_t buf[1<<14];size_t n;uint64_t len=0, checksum=FNV0;
    while((n=fread(buf,1,sizeof(buf),in))!=0){
      for(size_t i=0;i<n;i++){
        uint8_t c=buf[i];checksum=(checksum^c)*FNV_PRIME;
        unsigned prefix=1;
        for(unsigned j=0;j<8;j++){
          p->prepare(j,prefix);
          uint32_t prob=p->prob();
          unsigned bit=(c>>(7u-j))&1u;
          coder.put(bit,prob);p->observe(bit,prob);
          prefix=(prefix<<1)|bit;
        }
        p->advance(c);
      }
      len+=n;
    }
    if(ferror(in)||!coder.close())goto finish;
    int64_t end=ftello(out);
    if(end<sz)goto finish;
    uint64_t packed=uint64_t(end-sz);
    uint8_t footer[FOOTER];
    store64(footer,packed);store64(footer+8,len);
    store64(footer+16,checksum);
    memcpy(footer+24,MAGIC,8);
    // Mode stored in the most significant bit of length; verify safe cap on decode.
    if(adaptive)footer[15]|=0x80u;
    if(!enable_word)footer[15]|=0x40u;
    unsigned gate_code=min_support==8?3u:min_support==4?2u:min_support==2?1u:0u;
    footer[15]|=uint8_t(gate_code<<4);
    if(text_gate)footer[15]|=0x08u;
    if(enable_match)footer[15]|=0x04u;
    footer[15]|=uint8_t(match_style & 3u);
    if(!writeall(out,footer,FOOTER)||fflush(out)||fchmod(fileno(out),0755))goto finish;
    fprintf(stderr,"OMR6 mode=%s%s%s%s style=%u min_support=%u input=%llu payload=%llu binary=%lld archive=%llu\n",
      adaptive?"adaptive":"fixed",enable_word?"":"-noword",text_gate?"-textgate":"",enable_match?"-match":"",match_style,min_support,(unsigned long long)len,(unsigned long long)packed,
      (long long)sz,(unsigned long long)(sz+packed+FOOTER));
    status=0;
  }
 finish:
  fclose(in);if(fclose(out))status=1;
  if(status)remove(dst);
  return status;
}
static int decode(FILE* self,uint64_t packed,uint64_t orig,uint64_t wanted,bool adaptive,bool enable_word,unsigned min_support,bool text_gate,bool enable_match,unsigned match_style){
  int64_t end=filesize(self);if(end<0||packed>uint64_t(end-FOOTER))return err("Malformed archive size");
  if(fseeko(self,end-FOOTER-int64_t(packed),SEEK_SET))return err("Archive seek error");
  if(access("data9",F_OK)==0)return err("Refuse to overwrite existing data9");
  FILE* out=fopen("data9","wb");if(!out)return err("Cannot create data9");
  int status=1;uint64_t checksum=FNV0;
  {
    std::unique_ptr<Predictor> p(new Predictor(adaptive,enable_word,min_support,text_gate,enable_match));
    p->match_style=match_style;
    ArithmeticDecoder decoder(self,packed);
    uint8_t buf[1<<14];size_t used=0;
    for(uint64_t i=0;i<orig;i++){
      uint8_t c=0;unsigned prefix=1;
      for(unsigned j=0;j<8;j++){
        p->prepare(j,prefix);
        uint32_t prob=p->prob();
        unsigned bit=decoder.get(prob);
        c=uint8_t((c<<1)|bit);
        p->observe(bit,prob);prefix=(prefix<<1)|bit;
      }
      checksum=(checksum^c)*FNV_PRIME;p->advance(c);
      buf[used++]=c;
      if(used==sizeof(buf)){if(!writeall(out,buf,used))goto finish;used=0;}
    }
    if(!writeall(out,buf,used)||!decoder.br.ok || checksum!=wanted)goto finish;
    status=0;
  }
 finish:
  if(fclose(out))status=1;
  if(status){remove("data9");return err("Archive damaged or checksum mismatch");}
  fprintf(stderr,"OMR6 decoded exactly %llu bytes, checksum verified\n",(unsigned long long)orig);
  return status;
}
}  // namespace omr6
int main(int argc,char** argv){
  using namespace omr6;
  FILE* self=fopen("/proc/self/exe","rb");if(!self)return err("Cannot inspect own executable");
  int64_t size=filesize(self);int status=1;
  uint8_t footer[FOOTER];
  bool archive=size>=int64_t(FOOTER)&&fseeko(self,size-int64_t(FOOTER),SEEK_SET)==0
    &&fread(footer,1,FOOTER,self)==FOOTER&&memcmp(footer+24,MAGIC,8)==0;
  if(archive){
    bool adaptive=(footer[15]&0x80u)!=0;
    bool enable_word=(footer[15]&0x40u)==0;
    unsigned gate_code=(footer[15]>>4)&3u;
    unsigned min_support=gate_code==3?8u:gate_code==2?4u:gate_code==1?2u:0u;
    bool text_gate=(footer[15]&0x08u)!=0;
    bool enable_match=(footer[15]&0x04u)!=0;
    unsigned match_style=footer[15]&3u;
    footer[15]=0; // top original-size byte cannot be needed: 2e9 maximum accepted.
    if(match_style==3u || (match_style && !enable_match)){fclose(self);return err("Malformed prediction mode");}
    uint64_t n=load64(footer+8),packed=load64(footer);
    if(n>2'000'000'000ull || packed>uint64_t(size-int64_t(FOOTER)))status=err("Archive exceeds safe size");
    else status=decode(self,packed,n,load64(footer+16),adaptive,enable_word,min_support,text_gate,enable_match,match_style);
  }else{
    const char* src=argc>=2?argv[1]:"enwik9";
    const char* dst=argc>=3?argv[2]:"archive9";
    const char* mode=argc>=4?argv[3]:"adaptive-match-calib";
    bool adaptive=strncmp(mode,"adaptive",8)==0;
    bool text_gate=!strcmp(mode,"adaptive-textgate") || !strcmp(mode,"adaptive-match-textgate")||!strcmp(mode,"adaptive-match-calib")||!strcmp(mode,"adaptive-match-strong");
    bool enable_match=!strcmp(mode,"adaptive-match")||!strcmp(mode,"adaptive-match-textgate")||!strcmp(mode,"adaptive-match-calib")||!strcmp(mode,"adaptive-match-strong");
    unsigned match_style=!strcmp(mode,"adaptive-match-calib")?1u:!strcmp(mode,"adaptive-match-strong")?2u:0u;
    bool enable_word=(!strcmp(mode,"fixed") || !strcmp(mode,"adaptive") || !strcmp(mode,"adaptive-gate2") || !strcmp(mode,"adaptive-gate4") || !strcmp(mode,"adaptive-gate8") || text_gate || enable_match);
    unsigned gate=(!strcmp(mode,"adaptive-gate8")?8u:!strcmp(mode,"adaptive-gate4")?4u:!strcmp(mode,"adaptive-gate2")||text_gate||enable_match?2u:0u);
    if(strcmp(mode,"fixed")&&strcmp(mode,"adaptive")&&strcmp(mode,"fixed-noword")&&strcmp(mode,"adaptive-noword") && strcmp(mode,"adaptive-gate2")&&strcmp(mode,"adaptive-gate4")&&strcmp(mode,"adaptive-gate8")&&strcmp(mode,"adaptive-textgate")&&strcmp(mode,"adaptive-match")&&strcmp(mode,"adaptive-match-textgate")&&strcmp(mode,"adaptive-match-calib")&&strcmp(mode,"adaptive-match-strong"))status=err("Unsupported mode");
    else status=encode(self,src,dst,adaptive,enable_word,gate,text_gate,enable_match,match_style);
  }
  fclose(self);return status;
}