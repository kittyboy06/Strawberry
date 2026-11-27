/**
 * Calculates SHA-256 hex string of a File, Blob, or string using the browser Web Crypto API.
 */
export async function calculateSHA256(input: File | Blob | string): Promise<string> {
  let buffer: ArrayBuffer;
  if (typeof input === 'string') {
    const encoder = new TextEncoder();
    const encoded = encoder.encode(input);
    const copy = new Uint8Array(encoded.length);
    copy.set(encoded);
    buffer = copy.buffer;
  } else {
    buffer = await input.arrayBuffer();
  }
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}
