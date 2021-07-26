---
layout: post
title:  "DCO check failed"
date:   2021-06-18 12:36:35 +0800
categories: dco github
---
0x00 现象

有一天，在 GitHub 上提的 PR 遇到了 DCO 检查失败的问题，具体如下：

>   You only have one commit incorrectly signed off! To fix, first ensure you have a local copy of your branch by [checking out the pull request locally via command line](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/checking-out-pull-requests-locally). Next, head to your local branch and run:
>
>   ```
>   git commit --amend --no-edit --signoff
>   ```
>
>   Now your commits will have your sign off. Next run
>
>   ```
>   git push --force-with-lease origin 2106-test-DCO
>   ```
>
>   Commit sha: [bab823b](https://github.com/milvus-io/milvus/pull/5855/commits/bab823b7f5735a7f74d3ee69cda904f965d59b35), Author: Xiangyu Wang, Committer: GitHub; Expected "Xiangyu Wang [wxyucs@gmail.com](mailto:wxyucs@gmail.com)", but got "Xiangyu Wang [xiangyu.wang@zilliz.com](mailto:xiangyu.wang@zilliz.com)".

提示我说 PR 中有一个 commit 的提交者和 commit message 中的签名不一致，实际上我可以确定开发环境中的配置是正确的。



0x01 分析

之前见过这个错误，当时想办法绕过去了，这次又遇到正好深究一下。

目前的情况是：

-   我的 GitHub Primary email 是 `wxyucs@gmail.com`
-   这个 PR 的 head 分支是小A仓库的，我与他在这个分支上协作开发
-   DCO 检查这个 action 是开源的

我先从这个 GitHub Action 的源代码查起，在代码里找到了这段检查和报错代码：

```js
      if (!(authors.includes(sig.name.toLowerCase())) || !(emails.includes(sig.email.toLowerCase()))) {
        commitInfo.message = `Expected "${commit.author.name} <${commit.author.email}>", but got "${sig.name} <${sig.email}>".`
        failed.push(commitInfo)
      }
```

通过阅读上下文得知，`commit` 对象来自于 Git commit，`sig` 对象来自于 Git commit message 中的提取。目前 Git commit message 的内容是符合预期的，那么看来问题就出在 Git commit 上了。

我在本地拉取了这个 head 分支，用命令 `git blame --line-porcelain` 找到了那一行修改，看到的内容如下：

```makefile
bab823b7f5735a7f74d3ee69cda904f965d59b35 146 146 1
author Xiangyu Wang
author-mail <wxyucs@gmail.com>
author-time 1623988474
author-tz +0800
committer GitHub
committer-mail <noreply@github.com>
committer-time 1623988474
committer-tz +0800
summary Add a newline in README.md (#3)
previous 6a2cfe43155d578abdd6b162229c38007061205c Makefile
filename Makefile
```

这里可以看到 `author-mail` 已经错了，虽然这是我的邮箱，但不是这部分内容所需要的签名。另外，我注意到这里的 `committer` 是 GitHub，通过与小A交流得知，我往他仓库的 head 分支提交代码时，他使用了 *Squash and merge*。

到这里大致可以猜出错误的原因：我在本地开发提交时的签名是正确的。在往小A仓库的协作分支提交 PR 时，由于选择的是 *Squash and merge*，GitHub 用我的 GitHub Name 和 Primary email 作为作者的信息重新产生了一个 Git commit。所以在协作分支往主仓库提交 PR 时，检查到签名不匹配。而往常这个流程可用的原因是在协作分支上的 PR 使用的是 *Merge* 而不是 *Squash and merge*。



0x02 复现实验

有了以上的猜想，我按照如下步骤，果然复现了这个问题：

1.  从 `master` 分支新建一个开发分支 `dev`
2.  从 `dev` 分支上新建一个功能分支 `feature-update-readme`
3.  修改 readme，提交且签名（签上我的工作邮箱）
4.  在网页上创建一个 PR1，dev <- feature-update-readme
5.  在 PR1 的页面上，*Merge* 按键右边三角形点开，选择 *Squash and merge*
6.  在网页上再创建一个 PR2，master <- dev

在 PR2 的页面上可以看到，DCO 检查失败，发现 committer 与 signed-off 不一致。



0x03 结论与解决方案

如果只有一个开发身份的话，应当把 GitHub Name 和 Primary email 设置成与本地 Git config 内容一致。如果有公司、个人甚至更多开发身份的时候，需要避免在开发分支上做 squash merge。

如果已经遇到了这个问题，可以使用命令 `git commit --amend --author="Author Name <email@address.com> " --no-edit` 修改作者信息重新提交。



0x04 参考

https://docs.github.com/en/github/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request

https://docs.github.com/en/github/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges#rebase-and-merge-your-pull-request-commits