## PHỤ LỤC

### 3c.1: Dữ liệu từ điển âm tiết tiếng Việt

Thống kê từ điển thấy rằng từ tiếng Việt bao gồm:
* `16%` một âm tiết
* `71%` hai âm tiết
* `13%` là 3+ âm tiết

Nếu bỏ từ một âm tiết, thì số lượng 3+ âm tiết chiếm khoảng 15%.

=> _Cần dùng 2 data-structures để lưu dict (khoảng 100k từ):_

1/ Dùng`BinaryFuse(u16)` (cỡ `222KB`) để kiểm tra nhanh xem 1 chuỗi syllables có phải là 1 từ trong từ điển hay không?

2/ `IMF Trie` để auto-suggest âm tiết đang gõ dở

Có thể kết hợp với `Trigram Map & Filter` để reranking auto-suggest candidates

### IMF Trie

Thực chất trie cũng là 1 bảng băm tận dụng tính chất lặp lại có quy luật của văn viết. Nếu băm theo syllable thì tốc độ chậm vì số lượng node.children cao. Băm theo ký tự thì độ cao của cây là 6 (trung bình 6 ký tự / âm tiết), số lượng children cũng không ít vì TV gồm a-z và các kí tự có dấu:
 
 * 16 phụ âm `q,r,t,p,s,d,g,h,k,l,x,c,v,b,n,m`
 * 12 nguyên âm không thanh `a,â,ă,e,ê,y,u,ư,i,o,ô,ơ`
 * 60 nguyên âm có dấu (tổ hợp 5 dấu với 12 nguyên âm)
_=> Tổng 88 ký tự_


Dùng cách trình bày kiểu telex thì:

* 16 phụ âm `q,r,t,p,s,d,g,h,k,l,x,c,v,b,n,m`
* 06 nguyên âm không dấu `a,e,y,u,i,o`
* 02 ký tự hỗ trợ bỏ dấu `w,z`
* 02 ký tự hỗ trợ bỏ thanh `f,j`
_=> Tổng 26 ký tự_

Cách trình bày kiểu telex làm độ dài từ tăng lên trung bình gần 2 ký tự so với cách trình bày utf-8. Tức là khiến cây tìm kiếm càng dài hơn nữa. Trung bình 8 ký tự / âm tiết

Dùng phân tích ngữ âm để tách âm tiết TV thành `initial`, `middle`, `final+tone`. Số lượng các nodes là: 25 initial, 25 middle, và 42 final+tone. Độ cao của cây cho mỗi âm tiết là 3.

Tạo 3 loại nodes:

* `IntNode`: mảng children 25 con trỏ tới `MdlNode`
* `MdlNode`: mảng children 42 con trỏ tới `FnlhNode`
* `FnlNode`: mảng children 25 con trỏ tới `IntNode` và `u32` đếm số lần xuất hiện

=> IMF Trie :D


### N-gram Map & Filter

https://github.com/hexops/fastfilter#benchmarks

Dùng trigram để cân bằng giữa độ chính xác và số lượng gram count phải lưu trữ:
```
count=1 => `10_956_634` 3-grams => `12mb BinaryFuse(u8)`  (`x*9/(8*1024*1024)`)
count=2 => ` 2_345_545` 3-grams => ` 5mb BinaryFuse(u16)` (`x*18/(8*1024*1024)`)
remains => ` 4_000_183` 3-grams => `24mb HashCount`       (2^22 x 6-bytes)
TOTAL: 41MB,
```
=> Mỗi lookup cần đối chiếu với 2 filters và 1 hash_count. Cách này cân bằng giữa MEM và CPU!

#### Tiết kiệm bộ nhớ cho môi trường Web

Loại count = 1 và quantization về khoảng 8 nhóm để tiết kiệm MEM ta được:
```
o/ count=0,1
a/ count=02     => `2_343_228` 3-grams => `2.5 mb BinaryFuse(u8)`
b/ count=03..05 => `1_995_402` 3-grams => `4.3 mb BinaryFuse(u16)`
c/ count=06..11 => `  955_810` 3-grams => `2.0 mb BinaryFuse(u16)`
d/ count=12..25 => `  533_752` 3-grams => `1.2 mb BinaryFuse(u16)`
e/ count=25..80 => `  339_218` 3-grams => `0.7 mb BinaryFuse(u16)`
f/ remain       => `  174_532` 3-grams => `0.4 mb BinaryFuse(u16)`
   TOTAL: 11.1 MB
```
#### 2-gram
```
a/ count=1,2    => `1_444_334` 2-grams => `1.5 mb BinaryFuse(u8)`
b/ count=03..05 => `  424_429` 2-grams => `1.0 mb BinaryFuse(u16)`
c/ count=06..11 => `  276_007` 2-grams => `0.6 mb BinaryFuse(u16)`
d/ count=12..25 => `  199_301` 2-grams => `0.4 mb BinaryFuse(u16)`
e/ count=25..80 => `  170_952` 2-grams => `0.4 mb BinaryFuse(u16)`
f/ remain       => `  150_211` 2-grams => `0.3 mb BinaryFuse(u16)`
TOTAL: 4.2 MB
```

#### 4-gram
```
a/ count=2      => `4_407_945` 4-grams => `4.7 mb BinaryFuse(u8)`
b/ count=03..05 => `3_114_767` 4-grams => `6.7 mb BinaryFuse(u16)`
c/ count=06..11 => `1_252_778` 4-grams => `2.7 mb BinaryFuse(u16)`
d/ count=12..25 => `  601_206` 4-grams => `1.3 mb BinaryFuse(u16)`
e/ count=25..80 => `  322_523` 4-grams => `0.7 mb BinaryFuse(u16)`
f/ remain       => `  121_206` 4-grams => `0.3 mb BinaryFuse(u16)`
TOTAL: 16.4 MB
```

#### Cách tính điểm khi so khớp với chuỗi tokens đầu vào
```
o/ 01 điểm
a/ 02 điểm
b/ 04 điểm
c/ 08 điểm
d/ 16 điểm
e/ 32 điểm
f/ 64 điểm
```
=> !!! Cần đo xem cách tách thô này làm giảm độ hiệu quả của mô hình đi bao nhiêu ???
