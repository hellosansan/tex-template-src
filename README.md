# 基于《马克思恩格斯选集（第二版）》的 TeX 写作模版

## 命令

### 章节级别

```tex
\cover{path to cover}
  -> 封面

\tintro{标题}
  -> 前言（可选）

\tyear{标题}
  -> 年份标题（可选）

\tdoc{标题}
  -> 文献标题

\tpart{标题}
  -> 篇（可选）

\tchapter{标题}
  -> 章
\tchapternonum{标题}
  -> 无编号章

\tsection{标题}
  -> 节 1.
\tsectionnonum{标题}
  -> 无编号节 1.

\tsubsection{标题}
  -> 子节 A.
\tsubsectionnonum{标题}
  -> 无编号子节 A.

\tsubsubsection{标题}
  -> 小节 (1)
\tsubsubsectionnonum{标题}
  -> 无编号小节 (1)
```

### 注释级别

```tex
\nauthor{注释}
  -> 作者添加的注释

\neditor{注释}
  -> 编辑 / 译者添加的注释

\nend{注释}
  -> 尾注
```

### 段落级别

```tex
\hr{}
  -> 水平分割线

\quo{引文}
  -> 引用

\img{}
  -> 图像（）

\tbl{}

\todo{}

\info{}

\closing{}
```

### 字符级别

```tex
\important{}
\italic{}
\underdot{}
```
