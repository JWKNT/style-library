// Store-only ZIP writer. The download contains the original SVG bytes and notices.
const encoder = new TextEncoder();
const crcTable = Uint32Array.from({length: 256}, (_, n) => {
  for (let i = 0; i < 8; i++) n = (n & 1) ? 0xedb88320 ^ (n >>> 1) : n >>> 1;
  return n >>> 0;
});
export function crc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) crc = crcTable[(crc ^ byte) & 255] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}
export function makeZip(files) {
  const chunks = [], central = [];
  let offset = 0, centralSize = 0;
  for (const file of files) {
    const name = encoder.encode(file.name), bytes = file.bytes;
    const crc = crc32(bytes);
    const local = new Uint8Array(30 + name.length), lv = new DataView(local.buffer);
    lv.setUint32(0, 0x04034b50, true); lv.setUint16(4, 20, true);
    lv.setUint16(6, 0x0800, true); lv.setUint16(12, 0x5d49, true);
    lv.setUint32(14, crc, true); lv.setUint32(18, bytes.length, true); lv.setUint32(22, bytes.length, true);
    lv.setUint16(26, name.length, true); local.set(name, 30);
    const record = new Uint8Array(46 + name.length), rv = new DataView(record.buffer);
    rv.setUint32(0, 0x02014b50, true); rv.setUint16(4, 20, true); rv.setUint16(6, 20, true);
    rv.setUint16(8, 0x0800, true); rv.setUint16(14, 0x5d49, true);
    rv.setUint32(16, crc, true); rv.setUint32(20, bytes.length, true); rv.setUint32(24, bytes.length, true);
    rv.setUint16(28, name.length, true); rv.setUint32(42, offset, true); record.set(name, 46);
    chunks.push(local, bytes); central.push(record); centralSize += record.length;
    offset += local.length + bytes.length;
  }
  const end = new Uint8Array(22), view = new DataView(end.buffer);
  view.setUint32(0, 0x06054b50, true); view.setUint16(8, files.length, true); view.setUint16(10, files.length, true);
  view.setUint32(12, centralSize, true); view.setUint32(16, offset, true);
  return new Blob([...chunks, ...central, end], {type: 'application/zip'});
}
export function zipEntryName(slug, path) {
  return `${slug}/${path.startsWith('assets/Dropcaps/') ? path.split('/').at(-1) : path}`;
}
export async function downloadAlphabet(button) {
  if (button.disabled) return;
  const card = button.closest('.dropcap-set');
  const status = card.querySelector('.dropcap-status');
  button.disabled = true; button.setAttribute('aria-busy', 'true'); status.textContent = 'Preparing ZIP…';
  try {
    const slug = button.dataset.set;
    const paths = [...card.querySelectorAll('.dropcap-grid a')].map(a => a.getAttribute('href'));
    paths.push(...button.dataset.files.split(' ').filter(Boolean));
    const files = [];
    // Sequential reads keep the request count bounded on slow connections.
    for (const path of paths) {
      const response = await fetch(path);
      if (!response.ok) throw new Error('Download failed');
      files.push({name: zipEntryName(slug, path), bytes: new Uint8Array(await response.arrayBuffer())});
    }
    const url = URL.createObjectURL(makeZip(files));
    const link = document.createElement('a'); link.href = url; link.download = `${slug}-alphabet.zip`;
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
    status.textContent = 'ZIP ready.';
  } catch {
    status.textContent = 'ZIP could not download. Try again.';
  } finally {
    button.disabled = false; button.removeAttribute('aria-busy');
  }
}
if (typeof document !== 'undefined') {
  document.querySelectorAll('.dropcap-zip').forEach(button => button.addEventListener('click', () => downloadAlphabet(button)));
}
