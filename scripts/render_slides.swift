import Foundation
import PDFKit
import AppKit
guard CommandLine.arguments.count == 3 else { fatalError("Usage: render_slides.swift INPUT_DIR OUTPUT_DIST") }
let source = CommandLine.arguments[1]
let base = CommandLine.arguments[2]
for s in 1...12 {
 let id = String(format: "%02d", s)
 let url = URL(fileURLWithPath: "\(source)/Session \(id) DS Slides.pdf")
 guard let doc = PDFDocument(url: url) else { fatalError("Missing PDF") }
 let dir = "\(base)/slides/\(id)"
 try FileManager.default.createDirectory(atPath: dir, withIntermediateDirectories: true)
 for p in 0..<doc.pageCount {
  let page = doc.page(at: p)!
  let img = page.thumbnail(of: NSSize(width: 1440, height: 900), for: .mediaBox)
  let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
  let data = rep.representation(using: .jpeg, properties: [.compressionFactor:0.82])!
  try data.write(to: URL(fileURLWithPath: "\(dir)/\(p+1).jpg"))
 }
 print("Rendered \(id): \(doc.pageCount) pages")
}
