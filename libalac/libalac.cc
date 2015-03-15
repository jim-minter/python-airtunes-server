#include "ALACEncoder.h"

static AudioFormatDescription infd = {
  mSampleRate: 44100,
  mFormatID: kALACFormatLinearPCM,
  mFormatFlags: 12,
  mBytesPerPacket: 4,
  mFramesPerPacket: 1,
  mBytesPerFrame: 4,
  mChannelsPerFrame: 2,
  mBitsPerChannel: 16,
  mReserved: 0
};

static AudioFormatDescription outfd = {
  mSampleRate: 44100,
  mFormatID: kALACFormatAppleLossless,
  mFormatFlags: 1,
  mBytesPerPacket: 0,
  mFramesPerPacket: 352,
  mBytesPerFrame: 0,
  mChannelsPerFrame: 2,
  mBitsPerChannel: 0,
  mReserved: 0
};

extern "C" {
  ALACEncoder *
  init() {
    ALACEncoder *e = new ALACEncoder();
    e->SetFrameSize(outfd.mFramesPerPacket);
    e->InitializeEncoder(outfd);
    return e;
  }

  void
  encode(ALACEncoder *e, unsigned char *in, unsigned char *out, int *len) {
    e->Encode(infd, outfd, in, out, len);
  }
  
  void
  deinit(ALACEncoder *e) {
    delete e;
  }
}
