---
layout: post
title:  "How to Get Applications to Launch at System Startup on macOS"
date:   2022-03-19 23:32:00 +0800
categories: note macos
---

macOS provides a task management framework called **launchd**. You can create tasks by placing XML files in a specific directory. **launchd** will run the task at a specified time according to the configuration in the XML. It is suitable for automating customized tasks, such as starting a web server at startup, backing up files regularly, etc.

This is an example of starting a *Rails on Ruby* service at boot time.

**Preparation**

At first, determine the command to be run. In my case, the command to start *Rails on Ruby* is `
rails server --environment=development --binding=0.0.0.0 --port=4000 --using=puma`, and the work directory is `/Users/xyw/git/Today`.

**Create a Service**

Create a **plist** file in  `~/Library/LaunchAgents/` directory. This is my plist file to start rails: 

```xml
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.wxyucs.today</string>
        <key>KeepAlive</key>
        <true/>
        <key>RunAtLoad</key>
        <true/>
        <key>WorkingDirectory</key>
        <string>/Users/xyw/git/Today</string>
        <key>ProgramArguments</key>
        <array>
            <string>/Users/xyw/.rbenv/shims/rails</string>
            <string>server</string>
            <string>--environment=development</string>
            <string>--binding=0.0.0.0</string>
            <string>--port=4000</string>
            <string>--using=puma</string>
        </array>
        <key>StandardErrorPath</key>
        <string>/tmp/today.err</string>
        <key>StandardOutPath</key>
        <string>/tmp/today.out</string>
    </dict>
</plist>
```



**Enable the Service**

Now, enable the service:

```bash
$ launchctl load ~/Library/LaunchAgents/com.example.app.plist
$ launchctl start com.example.app
```

**Disable the Service**

If you no longer need this service at startup, you can disable with this command:

```bash
$ launchctl stop com.example.app
```

**Reference**

- https://www.launchd.info/
