干完活，日常摸鱼~

![][1]

一个Android开发交流群99+，点开看到在讨论：

![][2]

吼！原来是一位胖友的定时器代码，用到了 **`AsyncTask`** 被围观了~

**`AsyncTask`** 对很多老Android来说，是一个很有年代感的东西了，想当年毕业找工作，AsyncTask可是面试必问。

随着 **EventBus、RxJava、Kotlin协程** 等的出现，它渐渐淡出了我们的视野，面试八股文也少了它的身影，估计很多新晋的Android开发都没听过它。不禁感叹...

![][3]

发错，2333，感叹：技术的迭代真他么快啊，**学不动了**...

面试不问，但在一些老旧的项目中还有用到它的，索性也过一下吧，本节了解下废弃的原因，以及背后的实现原理~

----------

## 0x1、Deprecated 原因

AsyncTask，**Android(API 3)** 引入，**一个轻量级的异步任务库**，允许以 **非线程堵塞** 的方式执行操作。经过了好几个版本的调整：

- Android 1.6前，**串行执行**，原理：一个子线程进行任务的串行执行；
- Android 1.6到2.3，**并行执行**，原理：一个线程数为5的线程池并行执行，但如果前五个任务执行时间过长，会堵塞后续任务执行，故不适合大量任务并发执行；
- Android 3.0后，**串行执行**，原理：全局线程池进行串行处理任务；

真够折腾的，打开 [AsyncTask的官方文档][4] 一行橙字映入眼帘：

![][5]

> AsyncTask类在 Android 11(API 30) 中被废弃了，推荐使用java.util.concurrent或Kotlin协程来替代。

em...就废弃了啊，往下看是废弃原因的解释：

![][6]

大概意思：

> - AsyncTask本意是使得UI线程的使用变得简单正确，但最常见的用法是集成到UI中，反而导致了 **Context泄露、忘记回调、configuration变化Crash** 问题。
- 不同版本AsyncTask的兼容问题；
- 吞掉了来自doInBackground的异常；
- 不能提供比直接使用Executor更多的功能；
- Thread和Handler的辅助类，并非线程框架，主要用于执行一些时间不太长的异步任务；
- 用法复杂，三个通用参数(Params、Progress、Result) + 四个回调方法；

## 0x2、AsyncTask 用法详解

**Talk is cheap，show you the Code**，温习下它的用法吧：

```kotlin
    // 继承AsyncTask抽象类，建议声明为Activity的静态内部类，避免context泄露
    // 泛型参数依次为：
    // 
    // Params → 开始异步任务时传入的参数类型 → execute(Params)
    // Progress → 异步任务执行过程，返回进度值
    // Result → 异步任务执行完成后，返回结果类型 → doInBackground()
    // 
    class MyAsyncTask: AsyncTask<Task, Int, String>() {

        // 必须重写！在此执行耗时操作，返回执行结果
        override fun doInBackground(vararg params: Task?): String { return "执行耗时操作" }

        // 执行线程任务前的回调，即执行execute()前自动调用，常用作界面初始化操作
        override fun onPreExecute() { }

        // 在主线程中显示任务执行的进度，自动调用啊，按需重写
        override fun onProgressUpdate(vararg values: Int?) { }

        // 接受线程任务执行结果，线程任务结束时自动调用，可在此将结果更新到UI组件
        override fun onPostExecute(result: String?) { }

        // 异步任务被取消时自动调用，用于将异步任务设为取消状态，需在doInBackground()中停止
        // 此方法调用onPostExecute就不会被调用
        override fun onCancelled() {}
    }

    // 在主线程中初始化自定义AsyncTask实例后，调用execute(XXX)
    // 每个AsyncTask实例只能调用一次execute()，多次调用会抛出异常
    
    // 注①：Activity重建(如屏幕旋转)，之前持有的Activity引用已失效，任务正常运行，
    // 但任务执行完成后,在onPostExecute中修改UI不会生效，建议在Activity恢复的相关方法
    // 中重启AsyncTask任务；
    
    // 注②：最好在Activity、Fragment的onDestory()中调用AsyncTask.cancle()将AsyncTask设置
    // 为canceled状态，然后在doInBackground中去判断这个AsyncTask的status是否为：
    // AsyncTask.Status.RUNNING，是，直接返回，结束任务
}
```

em...用法看着，也不算很复杂，接着我们来了解下背后的原理(源码)~

## 0x3、精读源码

AsyncTask的源码才735行，非常简单，这次换个角度，不直接从构造方法开始跟，而是带着问题去跟：

- ① AsyncTask如何使用 **全局线程池** 实现 **串行执行**？线程池的参数配置是怎样的？
- ② 异步任务是怎么设计的？流转状态有哪些？多个异步任务怎么处理？有用到队列吗？还是其他数据结构？
- ③ 相关回调方法都是啥时候调用的？怎么做到在非UI线程中更新UI的？

### ① 线程池

先康康线程池，搜 **`Executor`**，吼，竟然有两个：**`THREAD_POOL_EXECUTOR`** 和 **`SERIAL_EXECUTOR`**：

![][7]

**`THREAD_POOL_EXECUTOR`** 规中矩初始化了一个 **`堵塞队列上限为128`** 的线程池，跟下另一个线程池的初始化方法：

![][8]

一个Runnable队列，在 **初始化后** 和 **一个任务执行结束后** 都会自动从这个队列中获取 **任务**，并通过 **THREAD_POOL_EXECUTOR** 线程池执行，以此实现了 **串行执行** (同步锁)。

另外，从开头的注释可以看到，其实AsyncTask也是支持 **并行执行** 的：

![][9]

调用下 **`executeOnExecutor(THREAD_POOL_EXECUTOR)`** 即可，就是不要中间商 **SerialExecutor**，而是直接用 **THREAD_POOL_EXECUTOR** 而已~

### ② 异步任务

从上面，我们知道了流转的是Runnable，跟下 **`execute()`** → **`executeOnExecutor`**

![][10]

关注上面的 **`mWorker`** 和 **`mFuture`** 跟到初始化它们的地方 → 构造方法，先是 **`mWorker`**：

![][11]

实现 **`Callable接口`**，定义了属性 **`mParams`**，实例化重写了**`call()`**方法，完成线程相关的设置，同时回调了 **doInBackground()** 方法。接着看下 **`mFuture`** ：

![][12]

任务包装类，添加了任务执行完后的回调，调用返回结果的处理方法，跟下：

![][13]

好吧，实际上都是调用的 **`postResult()`** 方法，就是用Handler，发送了一个标志为 **`MESSAGE_POST_RESULT`** 的 Message。难道是获取mainLooper，然后更新UI的套路？

### ③ Handler

往下跟，可以看到定义了一个静态内部类 **InternalHandler** ：

![][14]

处理两种类型的Message：

- **MESSAGE_POST_RESULT** → 任务结束；
- **MESSAGE_POST_PROGRESS** → 任务进度更新；

这里处理任务进度更新信息时，回调了 **`onProgressUpdate()`** ，再跟下 **`finish()`** ：

![][15]

判断任务取消的标记是否为真，是则回调 **`onCancelled()`** ，否则回调 **`onPostExecute()`**，最后将任务状态设置为 **`FINISHED`**。

到此，算是粗略过完AsyncTask的源码了，简要总结下要点：

**并行**：

- 线程池(最大容量128) 执行任务；
- 任务流转状态(待办、运行中、结束)；
- 任务的取消中断通过修改一个标志位实现，无论任务执行成功失败都会调用同一个处理方法；
- 通过Handler消息机制回调更新UI相关的回调；

**串行**

- 加多一个线程池，同步锁控制任务进队和出队，任务丢给另一个线程池处理，间接实现了任务的串行执行~


**参考文献**

- [带你轻松看源码---AsyncTask(异步任务)][16]
- [基于Android10.0代码深入了解终将老去的AsyncTask][17]
- [Android AsyncTask Deprecated, Now What?][18]



  [1]: http://static.zybuluo.com/coder-pig/w6jwgflb5v3os49tzts5xw6t/image_1fkhfbl02k6ibc11qd91rsf14174k.png
  [2]: http://static.zybuluo.com/coder-pig/7ajwyphic4pg4p71z1ftv3t6/image_1fk9jq70kqn4lu1162m48o4hp9.png
  [3]: http://static.zybuluo.com/coder-pig/kjug9l1twp03rbs18xgadt4h/image_1fk9kahl2n671cem1rq1gqoi2cm.png
  [4]: https://developer.android.com/reference/android/os/AsyncTask
  [5]: http://static.zybuluo.com/coder-pig/pkd2qml12yr7wq118qjmc41x/image_1fk9kii641ncm1d98ikj1dbep1l13.png
  [6]: http://static.zybuluo.com/coder-pig/g6uknjkniktaqfn1xbg1djh9/image_1fk9ljsrr1pkg13v7118u13jr1vro20.png
  [7]: http://static.zybuluo.com/coder-pig/tgvqxweobhlcxbars32iegn2/dfsdg.png
  [8]: http://static.zybuluo.com/coder-pig/t06sd1yt44ql81wd7bh65qfw/sdfsgA.png
  [9]: http://static.zybuluo.com/coder-pig/2mfcwaeu3dwy14poax3h9cmn/sdfg.png
  [10]: http://static.zybuluo.com/coder-pig/v5twjjfe6wvwok3tz33hb3sf/image_1fkj7miieoktvmm7okevb2c79.png
  [11]: http://static.zybuluo.com/coder-pig/on8oppk6q4xhkcgozw2183w9/45.png
  [12]: http://static.zybuluo.com/coder-pig/l5jhjgaglhv0k7vcj8nb6z46/ghl12.png
  [13]: http://static.zybuluo.com/coder-pig/nqm7prp9oymof409v6nxu7do/hfds23.png
  [14]: http://static.zybuluo.com/coder-pig/128pveqlq5s0kp1qd5me6o11/hhgfh.png
  [15]: http://static.zybuluo.com/coder-pig/jmtvms0y3i847vvc3b8lfzem/image_1fkhf1c64jh0ms11b7b1rkjapa3n.png
  [16]: https://blog.csdn.net/l540675759/article/details/62893318
  [17]: https://juejin.cn/post/6844904096068042765
  [18]: https://www.techyourchance.com/asynctask-deprecated/