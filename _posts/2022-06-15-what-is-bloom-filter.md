---
layout: post
title:  "What is Bloom filter"
date:   2022-06-15 01:26:00 +0800
categories: note bloomfilter
---
Bloom filter是一个概率数据结构，用于检测一个元素是否存在于一个集合中，特点是空间占用少、计算速度快。

<br>
**基本原理**

Bloom filter是一个数据结构，由一个长度为`m`的比特位数组和`k`个相互独立的哈希函数组成。每个哈希函数都可以将一个元素映射到数组的一个比特位上。
<br>
元素加入集合的方法是，先用哈希函数将这个元素映射到`k`个位置，而后将比特位数组中的这`k`个位置的值都置为`1`。显而易见，在确定哈希函数和元素的情况下，比特位数组中置为1 的位置也是确定的。
<br>
查询元素在集合中是否存在的方法是，先用哈希函数把元素映射成`k`个位置，然后再检查比特位数组中这`k`个位置的值。如果全是`1`则返回真，表示元素可能存在，相反则返回假，表示元素肯定不存在。
<br>
这里说元素可能存在是因为这`k`个位置的`1`可能是在别的元素加入集合时设置的，被查询元素可能不在集合中。其他元素写入导致查询结果为真但实际上元素不在集合中，这种情况叫误报（假阳性）。误报是有一定概率的，叫误报率（假阳性率）。

<br>
**误报率（假阳性率）**

误报率由元素数量`n`、比特位数组长度`m`和哈希函数数量`k`共同决定。
<br>
[误报率近似公式][1]：

![](https://wikimedia.org/api/rest_v1/media/math/render/svg/de73929baec5fd76dde95874189051648c635b1d)
<br>
简单来说，

- 元素数量越多，误报率越高
- 比特位数组越短，误报率越高
- 哈希函数越少，误报率越高

所以，提升比特位数组长度和哈希函数数量可以降低误报率。但是，提升数组长度和哈希函数数量的代价是，比特位数组越长，所需存储空间越大；哈希函数数量越多，每次插入和查询的过程就越慢。

<br>
**如何配置参数n、m、k？**

[使用n和m计算最优k值的公式][2]：

![](https://wikimedia.org/api/rest_v1/media/math/render/svg/fabc2770225ac59fe42a78f75ea89de650f0130c)

于是，可以通过以下步骤确定参数：

1. 确定集合的数据量`n`
2. 确定预期的存储大小`m`
3. 使用公式计算得到`k`
4. 使用`n`、`m`和`k`计算得到误报率
4. 若误报率太高，回到第2步通过提升`m`来调整
<br>
一些在线的Bloom filter参数计算器：

- https://hur.st/bloomfilter/
- https://krisives.github.io/bloom-calculator/

<br>
**应用**

在存储系统中，可以使用Bloom filter来判断一条记录是否在表中存在，从而减少磁盘I/O。例如，[BigTable论文][3]中提到了使用Bloom filter来优化读取操作：在BigTable中，读取操作需要访问所有的SSTable。若这些SSTable不在内存中，可能会产生多次磁盘访问。BigTable可以为每个SSTable都建立一个Bloom filter，这样可以快速地知道一条指定的数据在一个SSTable中是否存在，从而避免无效的磁盘访问。



[1]: <https://en.wikipedia.org/wiki/Bloom_filter#Probability_of_false_positives> "Probability of false positives"
[2]: <https://en.wikipedia.org/wiki/Bloom_filter#Optimal_number_of_hash_functions> "Optimal number of hash functions"
[3]: <https://static.googleusercontent.com/media/research.google.com/en//archive/bigtable-osdi06.pdf> "Bigtable: A Distributed Storage System for Structured Data"
