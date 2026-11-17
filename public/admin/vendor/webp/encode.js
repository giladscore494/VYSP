// Small wrapper around the libwebp encoder from @jsquash/webp 1.5.0 (Apache-2.0, see LICENSE.txt).
// Used only when the browser cannot produce WebP itself (Safari on iPhone, for example).
import factory from "./webp_enc.js";

const DEFAULTS = {
  quality: 82, target_size: 0, target_PSNR: 0, method: 4, sns_strength: 50,
  filter_strength: 60, filter_sharpness: 0, filter_type: 1, partitions: 0, segments: 4,
  pass: 1, show_compressed: 0, preprocessing: 0, autofilter: 0, partition_limit: 0,
  alpha_compression: 1, alpha_filtering: 1, alpha_quality: 100, lossless: 0, exact: 0,
  image_hint: 0, emulate_jpeg_size: 0, thread_level: 0, low_memory: 0, near_lossless: 100,
  use_delta_palette: 0, use_sharp_yuv: 0,
};

let modulePromise = null;

export async function encodeWebp(imageData, quality) {
  modulePromise ??= factory({ noInitialRun: true });
  const mod = await modulePromise;
  const out = mod.encode(imageData.data, imageData.width, imageData.height, { ...DEFAULTS, quality });
  if (!out) throw new Error("WebP encoding failed");
  return new Blob([out], { type: "image/webp" });
}
