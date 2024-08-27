# Overview
这是一个辅助阅读项目代码的工具，它会给出一个项目整体架构分析，以及每个项目文件具体的功能和分析
---
# Quick Strat
1. 在main.py处传入想要分析的项目的路径
2. 运行后在output文件夹里面找到分析的json文件
3. 运行frontend.py，可以上传第2步得到的json文件，得到更好的阅读体验

# TODO
1. 支持上传github / gitee链接，自动download文件
2. 拓展对于除了python之外其他编程语言的支持
3. 在项目整体结构的分析中，更结构化地列出各个部分功能，以及不同功能如何相互作用（通过哪个文件）。入口函数/文件是什么
4. 在每个项目文件具体分析中，举出输入和输出的例子
