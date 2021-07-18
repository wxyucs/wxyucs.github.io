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

由于之前在他人的 PR 上看到过这个内容，但是由于时间的原因也没有深究。这次遇到了正好解决一下。

目前能得到的信息是：

-   我的 GitHub 上 primary email 是 `wxyucs@gmail.com`
-   这个 PR 的 head 分支是我和另一个人协作的
-   DCO 检查这个 action 是开源的



我先从这个 GitHub Action 的源代码查起，我在代码里找到了这段检查和报错代码：

```js
      if (!(authors.includes(sig.name.toLowerCase())) || !(emails.includes(sig.email.toLowerCase()))) {
        commitInfo.message = `Expected "${commit.author.name} <${commit.author.email}>", but got "${sig.name} <${sig.email}>".`
        failed.push(commitInfo)
      }
```

通过阅读上下文得知，commit 对象来自于 git，sig 对象来自于 git commit message 中的提取。目前 git commit message 的内容是符合我的预期的，那么看来问题就出在 git commit 的信息上了。



我在本地开发环境拉取了这个 head 分支，用 git blame 命令找到了那一行修改，看到的内容如下：

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

这里可以看到 author-mail 已经错了，这是我的邮箱，但不是我开发这部分内容时所希望使用的签名。另外，我发现这里的 committer 是 GitHub，这也是一个异常点。



于是，我回顾了一下代码提交的流程，head分支在小A的仓库，我的代码不是直接push上去的，而是通过PR进去的。与往常不同的一点是，小A在合并这个PR的时候使用的不是我们通常用的merge，而是squash merge。



0x02 原因猜想

结合上我的 GitHub 配置看，这就是问题所在：

1.  我在自己仓库的一个分支上提交了一个 commit，使用了 -s 参数在 commit message 中加上了签名（signed-off
2.  我给小A仓库的协作分支提交了一个PR，他使用了 squash and merge
3.  GitHub 为这次 squash and merge 做了一次commit操作，并且留下信息，作者是我（我的GitHub Name和Primary Email），committer 是 GitHub
4.  在协作分支向主仓库提交 PR 的时候，DCO 发现这个commit上的信息和commit message里的签名不一致，检查失败



在 GitHub 上通过 PR 的方式产生的代码合并，背后实际上是 GitHub 帮你做了 `git merge`。

当 PR 中的合并参数选择是 merge 时，GitHub 会在 git history 上创建一个新的 merge 节点，这个节点没有任何实质上的内容，只是记录从另一个分支合并过来。

当 PR 中的合并参数选择是 squash 是，GitHub 会执行 `git merge - -squash` ，这个操作会把 head 分支上比 base 分支多的内容打包到一起，产生一个新的 commit，加到 base 分支的头部。

在 A 的仓库中提交的 PR 由于选择的是 squash merge，GitHub 为此创建了一个 commit，并且使用了 PR 作者的 GitHub 名字和邮箱作为 commit 的作者信息。这时，如果 A 在本地配置的名字和邮箱与GitHub上的名字和邮箱对不上，就会在 DCO 检查时报错。



0x03 复现实验

有了以上的猜想，我按照如下步骤，果然复现了这个问题：

1.  从 master 分支新建一个开发分支 dev
2.  从 dev 分支上新建一个功能分支 feature-update-readme
3.  修改 readme，提交且签名（签上我的工作邮箱）
4.  在网页上创建一个 Pull Request，dev <- feature-update-readme
5.  在Merge按键右边三角形点开，选择 squash and merge
6.  在网页上再创建一个 Pull Request，master <- dev

此时可以看到，DCO 检查失败，发现commuter与signed-off不一致。



0x04 结论与解决方案

如果只有一个开发身份的话，应当把 GitHub 上的名字和 Primary Email 设置成与本地 git config 内容一致。如果有公司、个人甚至更多开发身份的时候，需要避免在开发分支上做 squash merge，可以取而代之使用 merge 或者 rebase merge。

如果已经遇到了这个问题，可以使用命令 `git commit --amend --author="Author Name <email@address.com> " --no-edit` 来进行修改。





0x05 参考

https://docs.github.com/en/github/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request

https://docs.github.com/en/github/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges#rebase-and-merge-your-pull-request-commits