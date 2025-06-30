# Qidian Novel App Analysis Notes

Date: 2025/06/17

**Quick Navigation:**

* [1. Qidian App Request Logic](#1-qidian-app-request-logic)
* [2. `*.qd` File Structure and Content Analysis](#2-qd-file-structure-and-content-analysis)

## 1. Qidian App Request Logic

### 1. Header Fields

Field:
- `borgus`
- `cecelia`
- `cookie`
- `ywguid`
- `appId`
- ...
- `QDInfo`
- `gorgon`
- `ibex`
- `qdinfo`
- `qdsign`
- `tstamp`
- 
Among the values that change with each request are:

* `borgus`
* `cecelia`
* `cookie`
* `QDInfo`
* `ibex`
* `qdinfo`
* `qdsign`
* `tstamp`

These will not be analyzed in detail for now. Potentially useful reference materials:

* [iOS Reverse Engineering Notes](https://blog.csdn.net/weixin_44110940/article/details/141091917)

  * Lacks detailed steps
* [Qidian App Field Encryption Crack (Java)](https://www.cnblogs.com/HugJun/p/13503215.html)

  * Dated 2020-08-14
  * Java version
  * Includes: `QDInfo`, `QDSign`, `AegisSign`
* [Android Reverse Engineering Introduction: Network Request Parameter Analysis of a Certain Chinese App](https://www.jianshu.com/p/025bd308e857)

  * Dated 2020-08-05
  * Includes: `QDInfo`, `QDSign`, `AegisSign`
  * [Backup Link](https://www.52pojie.cn/thread-1239814-1-1.html)
* [QiDianHook](https://github.com/rwz657026189/QiDianHook)

  * Dated 2019-01-03
  * Not tested
* [appspiderHook](https://github.com/madking177/appspiderHook)

  * Dated 2023-12-11
  * Includes some hook functions
* [Frida Reimplementation of App Algorithm](https://www.wangan.com/p/11v71355c0c48670)

  * Dated 2023-01-11
  * Includes step-by-step process
* [Reversing a Signature Algorithm of a Certain App](https://bbs.kanxue.com/thread-271070.htm)

  * Dated 2022-01-07
  * Includes step-by-step process
  * Covers: `QDSign`
* [Qidian QDSign & AegisSign Reverse Engineering](https://www.jianshu.com/p/58ec69e04983)

  * Dated 2022-01-12
* [Extensive Algorithm Analysis of the Qidian Chinese App for Android](https://bbs.125.la/forum.php?mod=viewthread&tid=14053235)

  * Dated 2017-08-08

Note: Based on the analysis, these header fields are likely added by the `addRetrofitH` function in `com.qidian.QDReader.component.util.FockUtil`.

### 2. Overview of Key APIs

#### 2.1 Fetch Basic Book Information

* **Purpose**: Retrieves detailed information about a specific book.

* **URL**
  ```
  GET https://druidv6.if.qidian.com/argus/api/v3/bookdetail/lookfor
  ```

* **Query Parameters**:

  | Field     | Type | Required | Description                                   |
  | --------- | ---- | -------- | --------------------------------------------- |
  | bookId    | int  | Yes      | Unique ID of the Qidian book                  |
  | isOutBook | int  | No       | Whether the book is externally imported (0/1) |

* **Sample Params**:

  ```json
  {
    "bookId": 1234567,
    "isOutBook": 0
  }
  ```

#### 2.2 Retrieve List of Unpurchased Chapters

* **Purpose**: Fetches a list of chapters not yet purchased by the user, along with any chapter card information.

* **URL**

  ```
  POST https://druidv6.if.qidian.com/argus/api/v2/subscription/getunboughtchapterlist
  ```

* **Body Parameters**:

  | Field     | Type | Required | Description                               |
  | --------- | ---- | -------- | ----------------------------------------- |
  | bookId    | int  | Yes      | Book ID                                   |
  | pageSize  | int  | Yes      | Number of items per page (default: 99999) |
  | pageIndex | int  | Yes      | Page index, starting from 1               |

* **Sample Body**:

  ```json
  {
    "bookId": 1234567,
    "pageSize": 99999,
    "pageIndex": 1
  }
  ```

#### 2.3 Retrieve Purchased Chapter ID List

* **Purpose**: Retrieves a list of all purchased chapter IDs to help validate local cache.

* **URL**

  ```
  GET https://druidv6.if.qidian.com/argus/api/v3/chapterlist/chapterlist
  ```

* **Query Parameters**:

  | Field            | Type   | Required | Description                           |
  | ---------------- | ------ | -------- | ------------------------------------- |
  | bookId           | int    | Yes      | Book ID                               |
  | timeStamp        | long   | Yes      | Timestamp in milliseconds             |
  | requestSource    | int    | Yes      | Source identifier (e.g., 0 = App)     |
  | md5Signature     | string | Yes      | MD5 signature                         |
  | extendchapterIds | string | No       | Optional list of extended chapter IDs |

* **Sample Params**:

  ```json
  {
    "bookId": 1234567,
    "timeStamp": 1750000000000,
    "requestSource": 0,
    "md5Signature": "xxxxxxx",
    "extendchapterIds": 1234567
  }
  ```

#### 2.4 Retrieve Easter Egg Chapters

* **Purpose**: Retrieves a list of “Easter egg” chapters attached to the end of mainline chapters.

* **URL**

  ```
  GET https://druidv6.if.qidian.com/argus/api/v1/midpage/book/chapters
  ```

* **Query Parameter**: `bookId`

* **Sample Params**:

  ```json
  {
    "bookId": 1234567
  }
  ```

* **Sample Response**:

  ```json
  {
    "Data": {
      "Chapters": [
        {
          "ChapterId": 12345678,
          "MidpageList": [
            {"MidpageId": 8888, "MidpageName":"彩蛋1","UpdateTime":1686868686868},
            {"MidpageId": 9999, "MidpageName":"彩蛋2","UpdateTime":1686868687878}
          ]
        }
      ]
    }
  }
  ```
* **Field Description**

  * The `UpdateTime` field in `MidpageList` is in UTC milliseconds.
  * Can be used locally to assemble the reading order.

#### 2.5 Retrieve Easter Egg Chapter Content

* **Purpose**: Fetches the content of an “Easter egg” chapter.

* **URL**

  ```
  GET https://druidv6.if.qidian.com/argus/api/v3/midpage/pageinfo
  ```

* **Query Parameters**:

  | Field     | Type | Required | Description  |
  | --------- | ---- | -------- | ------------ |
  | bookId    | int  | Yes      | Book ID      |
  | chapterId | int  | Yes      | Chapter ID   |
  | needAdv   | int  | Yes      | Default is 0 |

* **Sample Params**:

  ```json
  {
    "bookId": 1234567,
    "chapterId": 12345678,
    "needAdv": 0
  }
  ```

#### 2.6 Download Chapter Content

* **VIP Chapter Download**

  * **URL**

    ```
    POST https://druidv6.if.qidian.com/argus/api/v4/bookcontent/getvipcontent
    ```

  * **Body**:

    | Field    | Description          |
    | -------- | -------------------- |
    | b        | bookId               |
    | c        | chapterId            |
    | ui       | userId               |
    | b-string | Encrypted package ID |

  * **Sample Body**:

    ```json
    {
        "b-string": "",
        "b": 1234567,
        "c": 555555,
        "ui": 0
    }
    ```

* **Secure Download**

  * **URL**

    ```
    GET https://druidv6.if.qidian.com/argus/api/v2/bookcontent/safegetcontent
    ```

  * **Query**: `bookId`, `chapterId`

  * **Sample Params**:

    ```json
    {
        "bookId": 1234567,
        "chapterId": 555555
    }
    ```

* **Batch Download**

  * **URL**

    ```
    POST https://druidv6.if.qidian.com/argus/newapi/v1/bookcontent/getcontentbatch
    ```

  * **Body**:

    ```json
    {
      "b": 1234567,
      "c": "555,222,333,444,666,888",
      "useImei": 0
    }
    ```

  * **Response** includes `DownloadUrl`, `Key`, `Md5`, and `Size`, which are used to download a ZIP file from a COS link. The file must then be unpacked locally.

---

## 2. `*.qd` File Structure and Content Analysis

### 1. Directory Structure

`*.qd` files are primarily used to store local cache data for the Qidian App. On Android, they are located in the following paths:

```sh
/data/media/0/Android/data/com.qidian.QDReader/files/QDReader/book/{user_id}/
```

or

```sh
/sdcard/Android/data/com.qidian.QDReader/files/QDReader/book/{user_id}/
```

or

```sh
/storage/emulated/0/Android/data/com.qidian.QDReader/files/QDReader/book/{user_id}/
```

The directory structure looks like this:

```sh
{user_id}/
│
├── {book_id}.qd               # Metadata file for the book
│
└── {book_id}/                 # Subdirectory containing chapter data
    ├── {chap_id}.qd           # Chapter data files
    ├── {chap_id}.qd
    └── ...
```

The following analysis is based on the sample code:

```python
from pathlib import Path
from pprint import pprint

book_id = "123456"
metadata_path = Path.cwd() / "data" / f"{book_id}.qd"
chap_dir = Path.cwd() / "data" / book_id
```

### 2. Parsing `{book_id}.qd`

#### 2.1 File Header Identification

Read the first 16 bytes to identify the file format:

```python
with open(metadata_path, "rb") as f:
    header = f.read(16)
    print(header)
```

Output:

```bash
b'SQLite format 3\x00'
```

This confirms the file is a SQLite 3 format database.

#### 2.2 Viewing Database Structure

Use the SQLite3 library to query the tables within the database:

```python
import sqlite3

conn = sqlite3.connect(metadata_path)
query = "SELECT name FROM sqlite_master WHERE type='table';"

cursor = conn.cursor()
cursor.execute(query)
tables = cursor.fetchall()
pprint(tables)

conn.close()
```

Example output:

```bash
[('chapter',),
 ('volume',),
 ('bookmark',),
 ('sqlite_sequence',),
 ('new_markline',),
 ('chapterExtraInfo',)]
```

#### 2.3 Sampling Table Data

Retrieve the first few entries from each table for inspection:

```python
conn = sqlite3.connect(metadata_path)
cursor = conn.cursor()

table_previews = {}

for (table_name,) in tables:
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 2;")
    rows = cursor.fetchall()
    table_previews[table_name] = rows

conn.close()

pprint(table_previews)
```

<details>
<summary>Sample output (click to expand)</summary>

```bash
{'bookmark': [],
 'chapter': [(-10000,
              'Copyright Info',
              0,
              None,
              0,
              1619200000000,
              0,
              '100',
              0,
              0,
              0,
              '0.0',
              None,
              None,
              None,
              None,
              0,
              -1,
              0,
              0,
              0,
              None,
              None,
              0,
              0),
             (111111111,
              'Chapter 1 Title',
              0,
              None,
              0,
              1619300000000,
              2345,                 # Content length
              '300',
              0,
              1000,
              0,
              '0.0',
              None,
              None,
              None,
              None,
              0,
              1619300000000,
              0,
              0,
              0,
              None,
              None,
              0,
              0)],
 'chapterExtraInfo': [],
 'new_markline': [],
 'sqlite_sequence': [],
 'volume': [('300', 'Section 1 Title'), ('301', 'Section 2 Title')]}
```

</details>

---

### 3. Parsing `{chap_id}.qd`

> Disclaimer: This is the author's first attempt at reverse engineering an Android app. The methods and ideas presented reflect personal understanding at this stage and are meant primarily for exploratory learning. Some techniques may have more optimal or standardized alternatives — feedback and discussion are welcome.

#### Tools and Dependencies Used

The following tools and libraries were used to analyze and extract content from chapter `.qd` files:

##### Reverse Engineering Tools

* [`jadx`](https://github.com/skylot/jadx/releases): Used to decompile APKs and extract Java layer logic
* [`Ghidra`](https://github.com/NationalSecurityAgency/ghidra/releases): For static analysis of native libraries (e.g., `.so` files)
* [`IDA Pro`](https://hex-rays.com/ida-pro/): Disassembler for static analysis of native code
* [`Android Platform Tools (adb)`](https://developer.android.com/tools/releases/platform-tools): For connecting to and debugging devices
* [`Frida`](https://github.com/frida/frida): Dynamic instrumentation and function hooking to help locate or invoke encryption logic

##### Python Dependencies

* `frida==16.7.19` and `frida-tools==13.7.1`

  * Versions 17.x and above currently have issues with the Java environment and require manual fixes
  * Related discussion: [Java is not defined](https://github.com/frida/frida/issues/3473)
* `pycryptodome`

  * Library for encryption and decryption algorithms

#### 3.1 ADB Connect to Device

Establish a connection to the target device using ADB:

```sh
adb connect <device-ip>
```

Use `adb devices` to verify the connection status.

#### 3.2 Configure `Frida`

##### Check Device Architecture

Run the following command to determine the device architecture:

```sh
adb shell getprop ro.product.cpu.abi
```

Common return values include:

* `x86`
* `x86_64`
* `arm64-v8a`

Download the appropriate `frida-server` based on the architecture and Frida Python version from [Frida Releases](https://github.com/frida/frida/releases), e.g.:

```
frida-server-16.7.19-android-x86.xz
```

##### Install and Grant Permissions

After extracting, rename the binary (e.g., to `frida-server-16.7.19`) and push it to the device:

```sh
adb push frida-server-16.7.19 /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server-16.7.19"
```

Start the service (requires `root` access):

```sh
adb shell
su
/data/local/tmp/frida-server-16.7.19 &
```

##### Verify Connection

Use the following command on your computer to list processes and confirm Frida is running:

```sh
frida-ps -U
```

If successful, you’ll see a list of processes on the device. Look for:

* `起点读书`
* `com.qidian.QDReader`

#### 3.3 Retrieve Native Logs

To assist with further analysis, export all `logcat` logs:

```sh
adb logcat > logs.txt
```

Later, filter by keywords to locate relevant entries.

#### 3.4 Hook Log Functions with Frida

During further analysis, the `jadx` decompiler revealed that the app uses Tencent’s open-source [Mars](https://github.com/Tencent/Mars) framework, specifically the `xlog` module for logging.

To capture raw debug information before encryption, you can write a Frida script to hook into the logging methods of the `Xlog` class for real-time log interception:

<details>
<summary>`hook_xlog.js` (click to expand)</summary>

```js
Java.perform(function () {
    const Xlog = Java.use("com.tencent.mars.xlog.Xlog");

    function hookLog(level, method) {
        if (!Xlog[method]) {
            console.log("Method not found:", method);
            return;
        }

        Xlog[method].overload('java.lang.String', 'java.lang.String', 'java.lang.String', 'int', 'int', 'long', 'long', 'java.lang.String')
            .implementation = function (tag, filename, funcname, line, pid, tid, maintid, msg) {
                const fullMsg = `[${level}][${tag}] ${msg}`;
                console.log(fullMsg);
                return this[method](tag, filename, funcname, line, pid, tid, maintid, msg);
            };
    }

    hookLog("V", "logV");
    hookLog("D", "logD");
    hookLog("I", "logI");
    hookLog("W", "logW");
    hookLog("E", "logE");
});
```

</details>

Execute the hook with:

```sh
frida -U -n 起点读书 -l hook_xlog.js
```

#### 3.5 Analyze Decryption Logic

After unpacking the APK, you can use `jadx` to decompile it and locate the core method under the `com/qidian/QDReader/component/bll` package.

<details>
<summary>Core decryption method `H(long, ChapterItem)` (click to expand)</summary>

<!-- (Insert decompiled code or analysis here if needed) -->

</details>

```java
public static ChapterContentItem H(long j10, ChapterItem chapterItem) throws Throwable {
    long j11;
    byte[] bArr;
    JSONObject jSONObject;
    String strEncode;
    long jCurrentTimeMillis = System.currentTimeMillis();
    ChapterContentItem chapterContentItem = new ChapterContentItem();
    String strF = F(j10, chapterItem);
    File file = new File(strF);
    d dVarW = W(file, chapterItem);
    if (dVarW == null) {
        h0("OKR_chapter_vip_null", String.valueOf(j10), String.valueOf(chapterItem.ChapterId), String.valueOf(-20076), "chapter data is null", "");
        chapterContentItem.setErrorCode(-20076);
        return chapterContentItem;
    }
    byte[][] bArr2 = dVarW.f18975search;
    if (bArr2 == null || bArr2.length < 2) {
        g0("OKR_chapter_vip_empty", j10, chapterItem, dVarW);
        chapterContentItem.setErrorCode(-20076);
        return chapterContentItem;
    }
    byte[] bArr3 = bArr2[0];
    byte[] bArr4 = bArr2[1];
    byte[] bArr5 = bArr2[2];
    byte[] bArr6 = bArr2[3];
    byte[] bArr7 = bArr2[4];
    long J = J(bArr3);
    if (J != 0 && J < vi.judian.e().f()) {
        chapterContentItem.setErrorCode(-20067);
        return chapterContentItem;
    }
    byte[] bArrX = x(bArr4, j10, chapterItem.ChapterId);
    if (bArrX == null) {
        if (file.exists()) {
            String strM = com.qidian.common.lib.util.m.m(file);
            strEncode = !TextUtils.isEmpty(strM) ? URLEncoder.encode(strM) : "";
        } else {
            strEncode = "file_not_found_" + strF;
        }
        d5.cihai.p(new AutoTrackerItem.Builder().setPn("OKR_chapter_vip_error").setDt("1103").setPdid(String.valueOf(j10)).setDid(String.valueOf(chapterItem.ChapterId)).setPdt(String.valueOf(strEncode.length())).setEx1(String.valueOf(QDUserManager.getInstance().k())).setEx2(QDUserManager.getInstance().s()).setEx3(QDUserManager.getInstance().t()).setEx4(we.d.I().d()).setEx5(strEncode).setAbtest("true").setKeyword("v2").buildCol());
        chapterContentItem.setErrorCode(-20068);
        return chapterContentItem;
    }
    String strW = w(bArrX);
    JSONObject jSONObjectQ = Q(strW);
    if (jSONObjectQ != null) {
        strW = jSONObjectQ.optString("content");
        int iOptInt = jSONObjectQ.optInt("type");
        int iOptInt2 = jSONObjectQ.optInt("code");
        String strOptString = jSONObjectQ.optString("msg");
        j11 = jCurrentTimeMillis;
        bArr = bArr7;
        e0.f18516search.a(j10, chapterItem.ChapterId, new e0.search(jSONObjectQ.optLong("idExpire"), jSONObjectQ.optInt("wt")));
        if (iOptInt2 != 0) {
            chapterContentItem.setErrorCode(iOptInt2);
            chapterContentItem.setErrorMessage(strOptString);
            return chapterContentItem;
        }
        if (TextUtils.isEmpty(strW)) {
            chapterContentItem.setErrorCode(-20088);
            return chapterContentItem;
        }
        String str = j10 + "_" + chapterItem.ChapterId;
        if (iOptInt == LockType.FOCK.getType()) {
            String strValueOf = String.valueOf(chapterItem.ChapterId);
            FockUtil fockUtil = FockUtil.INSTANCE;
            boolean zIsHasKey = fockUtil.isHasKey();
            Fock.FockResult fockResultUnlock = fockUtil.unlock(strW, strValueOf, str);
            if (fockResultUnlock.status == Fock.FockResult.STATUS_EMPTY_USER_KEY) {
                Fock.setup(we.d.X());
                fockResultUnlock = fockUtil.unlock(strW, strValueOf, str);
            }
            Fock.FockResult fockResult = fockResultUnlock;
            Logger.e("FockUtil: chapter_id:" + chapterItem.ChapterId + ",result:" + fockResult.status);
            if (fockResult.status != 0) {
                fockUtil.report(j10, chapterItem, fockResult, zIsHasKey);
            }
            int i10 = fockResult.status;
            if (i10 != 0) {
                if (i10 == -2) {
                    chapterContentItem.setErrorCode(-20079);
                    d5.cihai.p(new AutoTrackerItem.Builder().setPn("OKR_LoadChapterFailed_qimeiChanged").setEx1(String.valueOf(j10)).setEx2(String.valueOf(chapterItem.ChapterId)).buildCol());
                    return chapterContentItem;
                }
                if (i10 == Fock.FockResult.STATUS_EMPTY_USER_KEY) {
                    chapterContentItem.setErrorCode(-20082);
                    return chapterContentItem;
                }
                chapterContentItem.setErrorCode(-20080);
                return chapterContentItem;
            }
            strW = new String(fockResult.data, StandardCharsets.UTF_8);
        } else if (iOptInt != LockType.DEFAULT.getType()) {
            chapterContentItem.setErrorCode(-20081);
            return chapterContentItem;
        }
    } else {
        j11 = jCurrentTimeMillis;
        bArr = bArr7;
    }
    String str2 = strW;
    ArrayList<BlockInfo> arrayList = null;
    if (bArr5 != null) {
        try {
            jSONObject = new JSONObject(w(bArr5));
        } catch (Exception e10) {
            e10.printStackTrace();
        }
    } else {
        jSONObject = null;
    }
    chapterContentItem.setChapterContent(str2);
    chapterContentItem.setOriginalChapterContent(str2);
    chapterContentItem.setAuthorContent(jSONObject);
    if (bArr != null) {
        try {
            String strW2 = w(bArr);
            if (strW2 != null) {
                arrayList = (ArrayList) new Gson().j(strW2, new b().getType());
            }
        } catch (Exception e11) {
            e11.printStackTrace();
        }
        chapterContentItem.setBlockInfos(arrayList);
    }
    if (we.d.k0()) {
        StringBuffer stringBuffer = new StringBuffer();
        stringBuffer.append("Vip章节 内容读取 chapterId:");
        stringBuffer.append(chapterItem.ChapterId);
        stringBuffer.append(" chapterName:");
        stringBuffer.append(chapterItem.ChapterName);
        stringBuffer.append(" 读取, 耗时:");
        stringBuffer.append(System.currentTimeMillis() - j11);
        stringBuffer.append("毫秒");
        Logger.d("QDReader", stringBuffer.toString());
    }
    return chapterContentItem;
}
```
</details>

### Decryption Process Overview

The decryption process can be summarized as follows:

1. **File Chunk Reading**: The `W(file, ...)` function reads 5 chunks of data in little-endian format:

   ```
   [len0][part0][len1][part1]...[len4][part4]
   ```

2. **Stage One Decryption**: `part1` is passed to `x(...)`, which calls the native method `a.b.b(...)` and returns a JSON string.

3. **JSON Parsing**: Extracts fields such as `content`, `type`, `code`, `msg`, etc.

4. **VIP Chapter Secondary Decryption**: If `type == FOCK`, decryption proceeds via `FockUtil.unlock(...)`.

5. **Additional Data Block Handling**

---

#### 3.5.1 The `W` Function — Chunk Reading Logic

The core idea of the `W` function is to read five data chunks sequentially from a file input stream. Each chunk is preceded by a 4-byte little-endian integer indicating its length, followed by the corresponding number of bytes.

```java
FileInputStream fileInputStream;
byte[] bArr;
byte[] bArr2;
byte[] bArr3;
byte[] bArr4;
byte[] bArr5;
fileInputStream = new FileInputStream(file);
int iR = com.qidian.common.lib.util.m.r(fileInputStream);
bArr2 = new byte[iR];
fileInputStream.read(bArr2, 0, iR);
int iR2 = com.qidian.common.lib.util.m.r(fileInputStream);
bArr3 = new byte[iR2];
fileInputStream.read(bArr3, 0, iR2);
int iR3 = com.qidian.common.lib.util.m.r(fileInputStream);
bArr4 = new byte[iR3];
fileInputStream.read(bArr4, 0, iR3);
int iR4 = com.qidian.common.lib.util.m.r(fileInputStream);
bArr = new byte[iR4];
fileInputStream.read(bArr, 0, iR4);
int iR5 = com.qidian.common.lib.util.m.r(fileInputStream);
bArr5 = new byte[iR5];
fileInputStream.read(bArr5, 0, iR5);
dVar.f18975search = new byte[][]{bArr2, bArr3, bArr4, bArr, bArr5};
```

Here, `com.qidian.common.lib.util.m.r` is used to read a 4-byte length prefix and convert it to an `int`:

```java
public static int r(InputStream inputStream) throws IOException {
    byte[] bArr = new byte[4];
    inputStream.read(bArr);
    ByteBuffer byteBufferWrap = ByteBuffer.wrap(bArr);
    byteBufferWrap.order(ByteOrder.LITTLE_ENDIAN);
    return byteBufferWrap.getInt();
}
```

Thus, the overall file structure is:

```
[len0][data0]
[len1][data1]
[len2][data2]
[len3][data3]
[len4][data4]
```

---

#### Python Equivalent

You can reproduce this logic in Python using `BytesIO`:

```python
from io import BytesIO
from pathlib import Path

path = Path("xxx.qd")
with path.open('rb') as f:
    buf = BytesIO(f.read())

def read_chunk():
    # Read 4-byte little-endian length
    raw = buf.read(4)
    if len(raw) < 4:
        raise IOError("Incomplete file structure")
    length = int.from_bytes(raw, byteorder='little')
    # Read the actual data
    return buf.read(length)

chunk0 = read_chunk()
chunk1 = read_chunk()
chunk2 = read_chunk()
chunk3 = read_chunk()
chunk4 = read_chunk()
```

---

#### 3.5.2 The `x` Function — Native Decryption Logic

Looking into the `x` function reveals that it mainly calls a native JNI interface for decryption, such as:

```java
// private static byte[] x(byte[] bArr, long j10, long j11)
// ...
byte[] bArrB2 = a.b.b(j10, j11, bArr, QDUserManager.getInstance().k(), we.d.I().d());
if (bArrB2 != null) {
    return bArrB2;
}
```

Inside `a/b.java`, we find that this is a native method:

```java
public class b {
    static {
        try {
            System.loadLibrary("load-jni");
        } catch (Exception e10) {
            e10.printStackTrace();
        } catch (UnsatisfiedLinkError e11) {
            e11.printStackTrace();
        }
    }

    public static native byte[] b(long j10, long j11, byte[] bArr, long j12, String str);

    // ...
}
```

Using Ghidra to disassemble `libload-jni.so`, we can quickly locate the native implementation `Java_a_b_b`.

<details>
<summary>Snippet of `Java_a_b_b` implementation (click to expand)</summary>

<!-- (Insert Ghidra snippet here if needed) -->

</details>

```c
undefined8
Java_a_b_b(long *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,undefined8 param_5
          ,undefined8 param_6,undefined8 param_7,undefined8 param_8)
{
  // ...
  lVar5 = (**(code **)(*param_1 + 0x30))(param_1,&DAT_00100a57);
  if (((lVar5 != 0) && (lVar6 = (**(code **)(*param_1 + 0x30))(param_1,&DAT_00100a57), lVar6 != 0))
     && (lVar7 = (**(code **)(*param_1 + 0x30))(param_1,&DAT_00100a57), lVar7 != 0)) {
    __android_log_print(3,"QDReader_Jni","JNI:0");
    uVar8 = (**(code **)(*param_1 + 0x548))(param_1,param_7,0);
    __android_log_print(3,"QDReader_Jni","bookid: %s,chapterid: %s,userid: %s,imei: %s",__ptr,__src,
                        puVar1,uVar8);
    __android_log_print(3,"QDReader_Jni","JNI:1");
    __strcpy_chk(puVar2,puVar1,0xff);
    pcVar9 = (char *)__strcat_chk(puVar2,uVar8,0xff);
    __s = strcat(pcVar9,__src);
    sVar10 = strlen(__s);
    builtin_strncpy(pcVar9 + sVar10,"2EEE1433A152E84B3756301D8FA3E69A",0x21);
    __android_log_print(3,"QDReader_Jni","JNI:2");
    uVar11 = (**(code **)(*param_1 + 0x538))(param_1,puVar2);
    __android_log_print(3,"QDReader_Jni","JNI:3");
    lVar12 = (**(code **)(*param_1 + 0x388))
                       (param_1,lVar5,&DAT_00100a86,
                        "(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;");
    __android_log_print(3,"QDReader_Jni","JNI:4");
    if (lVar12 != 0) {
      __android_log_print(3,"QDReader_Jni","sha1id:%d",lVar12);
      __android_log_print(3,"QDReader_Jni","JNI:5");
      uVar13 = (**(code **)(*param_1 + 0x390))(param_1,lVar5,lVar12,param_7,uVar11);
      (**(code **)(*param_1 + 0x550))(param_1,uVar11,puVar2);
      __android_log_print(3,"QDReader_Jni","JNI:6");
      pcVar9 = (char *)(**(code **)(*param_1 + 0x548))(param_1,uVar13,0);
      __android_log_print(3,"QDReader_Jni","sha1key1 = %s",pcVar9);
      __android_log_print(3,"QDReader_Jni","JNI:7");
      sVar10 = strlen(pcVar9);
      if (0x17 < sVar10) {
        memset(&DAT_00104100,0,0x400);
        strncpy(&DAT_00104100,pcVar9,0x18);
      }
      __android_log_print(3,"QDReader_Jni","JNI:8 sha1key2:%s sha1key1:%s",&DAT_00104100,pcVar9);
      (**(code **)(*param_1 + 0x550))(param_1,uVar13,pcVar9);
      uVar11 = (**(code **)(*param_1 + 0x538))(param_1,&DAT_00104100);
      __android_log_print(3,"QDReader_Jni","JNI:9");
      __strcpy_chk(puVar3,&DAT_00104100,0xff);
      __strcat_chk(puVar3,uVar8,0xff);
      __android_log_print(3,"QDReader_Jni","JNI:10");
      uVar13 = (**(code **)(*param_1 + 0x538))(param_1,puVar3);
      __android_log_print(3,"QDReader_Jni","JNI:11");
      lVar5 = (**(code **)(*param_1 + 0x388))
                        (param_1,lVar6,&DAT_00100c2f,
                         "(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;");
      __android_log_print(3,"QDReader_Jni","JNI:12");
      if (lVar5 != 0) {
        __android_log_print(3,"QDReader_Jni","JNI:13");
        uVar14 = (**(code **)(*param_1 + 0x538))(param_1,puVar1);
        uVar15 = (**(code **)(*param_1 + 0x390))(param_1,lVar6,lVar5,uVar14,uVar13);
        (**(code **)(*param_1 + 0x550))(param_1,uVar13,puVar3);
        __android_log_print(3,"QDReader_Jni","JNI:14");
        pcVar9 = (char *)(**(code **)(*param_1 + 0x548))(param_1,uVar15,0);
        __android_log_print(3,"QDReader_Jni","JNI:15");
        sVar10 = strlen(pcVar9);
        if (sVar10 < 0x19) {
          __strcpy_chk(puVar4,pcVar9,0xff);
        }
        else {
          puVar4 = (undefined8 *)&DAT_00104100;
          memset(&DAT_00104100,0,0x400);
          strncpy(&DAT_00104100,pcVar9,0x18);
        }
        (**(code **)(*param_1 + 0x550))(param_1,uVar15,pcVar9);
        __android_log_print(3,"QDReader_Jni","JNI:16");
        uVar13 = (**(code **)(*param_1 + 0x538))(param_1,puVar4);
        __android_log_print(3,"QDReader_Jni","JNI:17");
        lVar5 = (**(code **)(*param_1 + 0x388))
                          (param_1,lVar7,&DAT_00100c72,"([BLjava/lang/String;)[B");
        __android_log_print(3,"QDReader_Jni","JNI:18");
        if (lVar5 != 0) {
          __android_log_print(3,"QDReader_Jni","JNI:19");
          uVar15 = (**(code **)(*param_1 + 0x390))(param_1,lVar7,lVar5,param_5,uVar13);
          __android_log_print(3,"QDReader_Jni","JNI:20");
          uVar11 = (**(code **)(*param_1 + 0x390))(param_1,lVar7,lVar5,uVar15,uVar11);
          __android_log_print(3,"QDReader_Jni","JNI:21");
          (**(code **)(*param_1 + 0x550))(param_1,param_7,uVar8);
          __android_log_print(3,"QDReader_Jni","JNI:22 %s",&DAT_00104100);
          __android_log_print(3,"QDReader_Jni","JNI:23");
          (**(code **)(*param_1 + 0x550))(param_1,uVar13,puVar4);
          __android_log_print(3,"QDReader_Jni","JNI:24");
          (**(code **)(*param_1 + 0x550))(param_1,uVar14,puVar1);
          __android_log_print(3,"QDReader_Jni","JNI:25");
          free(__ptr);
          __android_log_print(3,"QDReader_Jni","JNI:26");
          free(__src);
          __android_log_print(3,"QDReader_Jni","JNI:27");
          return uVar11;
        }
      }
    }
  }
  return 0;
}
```

`package a`:

```java
package a;

import android.content.Context;
import android.util.Base64;
import bf.cihai;
import com.qidian.QDReader.autotracker.bean.AutoTrackerItem;
import com.qidian.common.lib.Logger;
import com.qidian.common.lib.util.q0;
import java.security.NoSuchAlgorithmException;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public class b {
    private static final String CHARSET_ASCII = "ascii";
    private static final String MAC_SHA1_NAME = "HmacSHA1";

    static {
        try {
            System.loadLibrary("load-jni");
        } catch (Exception e10) {
            e10.printStackTrace();
        } catch (UnsatisfiedLinkError e11) {
            e11.printStackTrace();
        }
    }

    public static native byte[] b(long j10, long j11, byte[] bArr, long j12, String str);

    public static native void c(Context context);

    public static byte[] d(byte[] bArr, String str) {
        try {
            return cihai.search(bArr, str);
        } catch (Exception e10) {
            Logger.exception(e10);
            return null;
        }
    }

    private static String encryptToSHA1(String str, String str2) throws Exception {
        SecretKeySpec secretKeySpec = new SecretKeySpec(str.getBytes(CHARSET_ASCII), MAC_SHA1_NAME);
        Mac mac = Mac.getInstance(MAC_SHA1_NAME);
        mac.init(secretKeySpec);
        return new String(Base64.encode(mac.doFinal(str2.getBytes(CHARSET_ASCII)), 0));
    }

    public static String m(String str, String str2) {
        String str3;
        try {
            str3 = bf.a.judian(str, str2);
        } catch (NoSuchAlgorithmException e10) {
            e = e10;
            str3 = null;
        }
        try {
            if (str3.length() != 24) {
                d5.cihai.p(new AutoTrackerItem.Builder().setPn("OKR_b_m").setEx1(String.valueOf(str3.length())).setEx2(str + "/" + str2 + "/" + str3).buildCol());
            }
        } catch (NoSuchAlgorithmException e11) {
            e = e11;
            Logger.exception(e);
            return str3;
        }
        return str3;
    }

    public static String s(String str, String str2) {
        String str3;
        try {
            str3 = encryptToSHA1(str, str2);
            try {
                if (str3.length() >= 24) {
                    return str3;
                }
                d5.cihai.p(new AutoTrackerItem.Builder().setPn("OKR_b_s").setEx1(String.valueOf(str3.length())).setEx2(str + "/" + str2 + "/" + str3).buildCol());
                return q0.m(str3, 24, (char) 0);
            } catch (Exception e10) {
                e = e10;
                Logger.exception(e);
                return str3;
            }
        } catch (Exception e11) {
            e = e11;
            str3 = null;
        }
    }
}
```

`q0.m`:

```java
public static String m(String str, int i10, char c10) {
    StringBuilder sb = new StringBuilder();
    sb.append(str);
    int length = i10 - str.length();
    for (int i11 = 0; i11 < length; i11++) {
        sb.append(c10);
    }
    return sb.toString();
}
```

`package bf`:

```java
import com.qidian.QDReader.qmethod.pandoraex.monitor.c;
import com.qidian.common.lib.Logger;
import java.nio.charset.StandardCharsets;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class cihai {

    /* renamed from: search, reason: collision with root package name */
    private static final String f1806search = "bf.cihai";

    public static String cihai(String str, String str2) throws Exception {
        IvParameterSpec ivParameterSpec = new IvParameterSpec(new byte[8]);
        byte[] bytes = str2.getBytes("UTF-8");
        if (bytes.length == 16) {
            byte[] bArr = new byte[24];
            System.arraycopy(bytes, 0, bArr, 0, 16);
            System.arraycopy(bytes, 0, bArr, 16, 8);
            bytes = bArr;
        }
        SecretKeySpec secretKeySpec = new SecretKeySpec(bytes, "DESede");
        Cipher cipher = Cipher.getInstance("DESede/CBC/PKCS5Padding");
        if (cipher == null) {
            return "";
        }
        cipher.init(1, secretKeySpec, ivParameterSpec);
        return search.judian(c.search(cipher, str.getBytes()));
    }

    public static String judian(byte[] bArr, String str) throws Exception {
        IvParameterSpec ivParameterSpec = new IvParameterSpec("01234567".getBytes(StandardCharsets.UTF_8));
        byte[] bytes = str.getBytes("UTF-8");
        if (bytes.length == 16) {
            byte[] bArr2 = new byte[24];
            System.arraycopy(bytes, 0, bArr2, 0, 16);
            System.arraycopy(bytes, 0, bArr2, 16, 8);
            bytes = bArr2;
        }
        SecretKeySpec secretKeySpec = new SecretKeySpec(bytes, "DESede");
        Cipher cipher = Cipher.getInstance("DESede/CBC/PKCS5Padding");
        if (cipher == null) {
            return "";
        }
        cipher.init(1, secretKeySpec, ivParameterSpec);
        return search.judian(c.search(cipher, bArr));
    }

    public static byte[] search(byte[] bArr, String str) throws Exception {
        if (bArr != null && str != null) {
            IvParameterSpec ivParameterSpec = new IvParameterSpec(new byte[8]);
            byte[] bytes = str.getBytes("UTF-8");
            if (bytes != null && bytes.length >= 1) {
                if (bytes.length == 16) {
                    byte[] bArr2 = new byte[24];
                    System.arraycopy(bytes, 0, bArr2, 0, 16);
                    System.arraycopy(bytes, 0, bArr2, 16, 8);
                    bytes = bArr2;
                }
                Cipher cipher = Cipher.getInstance("DESede/CBC/PKCS5Padding");
                if (cipher == null) {
                    Logger.e(f1806search, "cipher is null");
                    return null;
                }
                cipher.init(2, new SecretKeySpec(bytes, "DESede"), ivParameterSpec);
                try {
                    return c.search(cipher, bArr);
                } catch (Exception e10) {
                    e10.printStackTrace();
                    int length = bArr.length;
                    Logger.e(f1806search, "decryptDES失败：" + str + "," + length);
                    return null;
                }
            }
            Logger.e(f1806search, "keyBytes is illegal");
        }
        return null;
    }
}
```

</details>

### Unexpected Discovery in Function

Inside the function, it was unexpectedly discovered that numerous calls to `__android_log_print` were used to output intermediate variables (such as decryption parameters / keys, etc.).

This means it's possible to view critical information involved in the decryption process directly through `logcat`, without needing to hook functions.

As a result, we revisited the previously exported `logs.txt` file and quickly located the relevant log entries using keyword searches:

```log
06-01 12:00:00.000  1234  4321 D QDReader_Jni: bookid: ****,chapterid: ***,userid: **,imei: ****
...
06-01 12:00:00.000  1234  4321 D QDReader_Jni: sha1id:****
...
06-01 12:00:00.000  1234  4321 D QDReader_Jni: sha1key1 = ****base64-key****
...
06-01 12:00:00.000  1234  4321 D QDReader_Jni: JNI:8 sha1key2:****key2**** sha1key1:****key1****
...
06-01 12:00:00.000  1234  4321 D QDReader_Jni: JNI:22 ****
```

Based on the log output and analysis of `Java_a_b_b` in Ghidra, an equivalent Python implementation of the decryption logic can be reconstructed as follows:

```python
import hashlib
import hmac
from base64 import b64encode
from Crypto.Cipher import DES3
from Crypto.Util.Padding import unpad

def sha1_hmac(key: str, data: str) -> str:
    digest = hmac.new(key.encode(), data.encode(), hashlib.sha1).digest()
    return b64encode(digest).decode()[:24]

def md5_hmac(key: str, data: str) -> str:
    digest = hmac.new(key.encode(), data.encode(), hashlib.md5).digest()
    return b64encode(digest).decode()[:24]

def des3_decrypt(data: bytes, secret: str) -> bytes:
    """3DES/CBC decryption"""
    cipher = DES3.new(secret.encode(), DES3.MODE_CBC, b'\x00' * 8)
    decrypted = cipher.decrypt(data)
    return unpad(decrypted, block_size=8)

def decrypt_content(cid: str, chunk1: bytes, uid: str, imei: str) -> str:
    """
    - Perform two-layer 3DES decryption on chunk1
    """
    # Compute both keys
    sec1 = sha1_hmac(
        imei,
        uid + imei + cid + "2EEE1433A152E84B3756301D8FA3E69A",
    )
    sec2 = md5_hmac(uid, sec1 + imei)

    # Decrypt
    raw = chunk1
    step1 = des3_decrypt(raw, sec2)
    step2 = des3_decrypt(step1, sec1)

    return step2.decode("utf-8", errors="ignore")  # or "replace"
```

---

### 3.5.3 `fockUtil.unlock` Function

During analysis of the `unlock` function, it was revealed to be another native method:

<details>
<summary>`com.yuewen.fock` (Click to expand)</summary>

```java
package com.yuewen.fock;

public class Fock {
    public static class FockResult {
        public static int STATUS_BAD_DATA = -1;
        public static int STATUS_EMPTY_USER_KEY = -3;
        public static int STATUS_MISSING_KEY_POOL = -2;
        public static int STATUS_SUCCESS;
        public final byte[] data;
        public final int dataSize;
        public final int status;

        public FockResult(int i10, byte[] bArr, int i11) {
            this.status = i10;
            this.data = bArr;
            this.dataSize = i11;
        }
    }

    static {
        System.loadLibrary("fock");
        ignoreBlockPattern = Pattern.compile(ignoreBlockPatternString);
    }

    public static void addKeys(String str, String str2) {
        byte[] bArrDecode = Base64.decode(str, 0);
        ReentrantLock reentrantLock = lock;
        reentrantLock.lock();
        try {
            ak(bArrDecode, bArrDecode.length, str2.getBytes());
            reentrantLock.unlock();
        } catch (Throwable th2) {
            lock.unlock();
            throw th2;
        }
    }
    private static native void ak(byte[] bArr, int i10, byte[] bArr2);

    public static void setup(String str) {
        ReentrantLock reentrantLock = lock;
        reentrantLock.lock();
        try {
            it(str.getBytes(), str.length());
            reentrantLock.unlock();
        } catch (Throwable th2) {
            lock.unlock();
            throw th2;
        }
    }
    private static native int it(byte[] bArr, int i10);

    public static FockResult unlock(String str, String str2, String str3) {
        byte[] bArrDecode = Base64.decode(str, 0);
        ReentrantLock reentrantLock = lock;
        reentrantLock.lock();
        try {
            FockResult fockResultUksf = uksf(bArrDecode, bArrDecode.length, str2.getBytes(), str2.length(), str3.getBytes());
            reentrantLock.unlock();
            return fockResultUksf;
        } catch (Throwable th2) {
            lock.unlock();
            throw th2;
        }
    }
    private static native FockResult uksf(byte[] bArr, int i10, byte[] bArr2, int i11, byte[] bArr3);
}
```

</details>

---

### Method 1: Hooking with `Frida`

> ⚠️ Note: Before executing this hook, ensure that the app is launched on the device and a VIP chapter is opened. This guarantees that the target class and methods (such as `Fock`) have been loaded and initialized; otherwise, the hook will not work.

<details>
<summary>`hook_fock.js` (Click to expand)</summary>

```js
rpc.exports = {
    unlock: function (arg1, arg2, arg3) {
        return new Promise(function (resolve, reject) {
            Java.perform(function () {
                try {
                    var TargetClass = Java.use('com.yuewen.fock.Fock');
                    var StringClass = Java.use('java.lang.String');
                    var CharsetClass = Java.use('java.nio.charset.Charset');

                    var result = TargetClass.unlock(arg1, arg2, arg3);
                    var status = result.status.value;

                    var utf8Charset = CharsetClass.forName("UTF-8");
                    var javaStr = StringClass.$new(result.data.value, utf8Charset);
                    var contentStr = javaStr.toString();

                    resolve(JSON.stringify({
                        status: status,
                        content: contentStr
                    }));
                } catch (e) {
                    resolve(JSON.stringify({
                        status: -999,
                        error: e.toString()
                    }));
                }
            });
        });
    }
};
```

</details>

With this setup, the `unlock` method can now be invoked directly from Python via `Frida RPC`. Example usage coming next.

```python
import frida

def test():
    book_id = "1111111111"
    chap_id = "2222222222"
    content = "xxx..."  # Encrypted content to be decrypted

    device = frida.get_device("your.device.ip.address")
    # Alternatively, use frida.get_usb_device()
    session = device.attach("起点读书")  # Attach to the Qidian app

    with open("hook_fock.js", "r", encoding="utf-8") as f:
        jscode = f.read()

    script = session.create_script(jscode)
    script.load()

    print("[*] Script loaded. Starting unlock tasks...")
    key_1 = chap_id
    key_2 = f"{book_id}_{chap_id}"
    # Call Frida RPC synchronously
    raw = script.exports_sync.unlock(content, key_1, key_2)
    print(raw)

if __name__ == "__main__":
    test()
```

---

### Option 2: Reverse Engineering and Custom Implementation

Begin by using `Frida` to hook and analyze the methods related to the `Fock` class:

<details>
<summary>Hook Script (click to expand)</summary>

```js
// hook_fock_v2.js
var indentMap = {};

function getIndent(threadId) {
    var lvl = indentMap[threadId] || 0;
    return Array(lvl + 1).join('  ');
}

Java.perform(function () {
    const Thread = Java.use("java.lang.Thread");
    const fockClass = Java.use("com.yuewen.fock.Fock");

    const methods = fockClass.class.getDeclaredMethods();
    methods.forEach(function (method) {
        const name = method.getName();
        try {
            const overloads = fockClass[name].overloads;
            overloads.forEach(function (overload) {
                overload.implementation = function () {
                    const tid = Thread.currentThread().getId().toString();

                    indentMap[tid] = (indentMap[tid] || 0) + 1;
                    console.log(getIndent(tid) + "-> Enter: " + this.$className + "." + name);

                    for (let i = 0; i < arguments.length; i++) {
                        console.log(getIndent(tid) + "Arg[" + i + "]: " + arguments[i]);
                    }

                    var result, exception = null;
                    try {
                        result = this[name].apply(this, arguments);
                    } catch (e) {
                        exception = e;
                    } finally {
                        if (exception) {
                            console.log(getIndent(tid) + "<- Exception: " + exception);
                        } else {
                            console.log(getIndent(tid) + "<- Exit:  " + this.$className + "." + name
                                        + " => " + result);
                        }
                        indentMap[tid]--;
                        if (indentMap[tid] === 0) {
                            delete indentMap[tid];
                        }
                    }

                    if (exception) throw exception;
                    return result;
                };
            });
        } catch (e) {
            console.log("Could not hook " + name + ": " + e);
        }
    });
});
```

```python
import frida
import sys

PACKAGE_NAME = "com.qidian.QDReader"

device = frida.get_device("...")

pid = device.spawn([PACKAGE_NAME])
session = device.attach(pid)

with open("hook_fock_v2.js", encoding="utf-8") as f:
    script = session.create_script(f.read())

script.on("message", lambda msg, data: print("[FRIDA]", msg))
script.load()

device.resume(pid)
print("[*] Hook started. Ctrl+C to stop.")
sys.stdin.read()
```

</details>

---

Next, open `libfock.so` using the **64-bit version of IDA Pro**.

According to reverse engineering best practices, the first step is to locate the `JNI_OnLoad(JavaVM *vm, void *reserved)` function.

<details>
<summary>`JNI_OnLoad` (click to expand)</summary>

```c
jint JNI_OnLoad(JavaVM *vm, void *reserved)
{
  jint v2; // w19
  __int64 v4; // x8
  __int64 v5; // x0
  __int64 v6; // x20
  __int64 v7; // [xsp+8h] [xbp-188h] BYREF
  __int128 dest[20]; // [xsp+10h] [xbp-180h] BYREF
  __int64 v9[4]; // [xsp+150h] [xbp-40h] BYREF

  v9[3] = *(_QWORD *)(_ReadStatusReg(ARM64_SYSREG(3, 3, 13, 0, 2)) + 40);
  v2 = 65542;
  if ( (*vm)->GetEnv(vm, (void **)&v7, 65542LL) )
    return -1;
  v4 = 0LL;
  memset(v9, 0, 21);
  do
  {
    dest[0] = xmmword_1BD00;
    *((_BYTE *)v9 + v4) = *(_BYTE *)((unsigned __int64)dest | v4 & 0xF) ^ byte_1BE21[v4];
    ++v4;
  }
  while ( v4 != 20 );
  v5 = (*(__int64 (__fastcall **)(__int64, __int64 *, long double))(*(_QWORD *)v7 + 48LL))(
         v7,
         v9,
         *(long double *)&xmmword_1BD00);
  if ( !v5 )
    return -1;
  v6 = v5;
  memcpy(dest, off_24408, 0x138u);
  if ( (*(unsigned int (__fastcall **)(__int64, __int64, __int128 *, __int64))(*(_QWORD *)v7 + 1720LL))(
         v7,
         v6,
         dest,
         13LL) )
  {
    return -1;
  }
  qword_26058 = (unsigned __int64)&qword_26058 ^ (unsigned __int64)fock_43254543;
  qword_26060 = (unsigned __int64)&qword_26060 ^ (unsigned __int64)fock_uk;
  qword_26070 = (unsigned __int64)&qword_26070 ^ (unsigned __int64)fock_uksf;
  qword_26068 = (unsigned __int64)&qword_26068 ^ (unsigned __int64)fock_sn;
  return v2;
}
```

`xmmword_1BD00` data:

```
.rodata:000000000001BD00 76 36 31 6F 75 61 6B 70 67 34+xmmword_1BD00 DCB 0x76, 0x36, 0x31, 0x6F, 0x75, 0x61, 0x6B, 0x70, 0x67, 0x34, 0x69, 0x7A, 0x6D, 0x35, 0x32, 0x77
.rodata:000000000001BD00 69 7A 6D 35 32 77                                                     ; DATA XREF: JNI_OnLoad:loc_937C↑o
.rodata:000000000001BD00                                                                       ; JNI_OnLoad+74↑r
```

`byte_1BE21` data:

```
.rodata:000000000001BE21 15 59 5C 40 0C 14 0E 07 02 5A+byte_1BE21 DCB 0x15, 0x59, 0x5C, 0x40, 0xC, 0x14, 0xE, 7, 2, 0x5A, 0x46, 0x1C, 2, 0x56, 0x59, 0x58, 0x30, 0x59
.rodata:000000000001BE21 46 1C 02 56 59 58 30 59 52 04+                                        ; DATA XREF: JNI_OnLoad+78↑o
.rodata:000000000001BE21 00 00 00                                                              ; JNI_OnLoad+80↑o
```

`off_24408` data:

```
.data.rel.ro:0000000000024408 3F BD 01 00 00 00 00 00       off_24408 DCQ aIt                       ; DATA XREF: JNI_OnLoad+D0↑o
.data.rel.ro:0000000000024408                                                                       ; JNI_OnLoad+D8↑o
.data.rel.ro:0000000000024408                                                                       ; "it"
.data.rel.ro:0000000000024410 42 BD 01 00 00 00 00 00       DCQ aBiI                                ; "([BI)I",0
.data.rel.ro:0000000000024418 70 89 00 00 00 00 00 00       DCQ sub_8970
.data.rel.ro:0000000000024420 49 BD 01 00 00 00 00 00       DCQ aAk                                 ; "ak"
.data.rel.ro:0000000000024428 4C BD 01 00 00 00 00 00       DCQ aBiBV                               ; "([BI[B)V",0
.data.rel.ro:0000000000024430 58 8A 00 00 00 00 00 00       DCQ sub_8A58
.data.rel.ro:0000000000024438 55 BD 01 00 00 00 00 00       DCQ aUk                                 ; "uk"
.data.rel.ro:0000000000024440 58 BD 01 00 00 00 00 00       DCQ aBiBiLcomYuewen                     ; "([BI[BI)Lcom/yuewen/fock/Fock",0x24,"FockResult;",0
.data.rel.ro:0000000000024448 64 8B 00 00 00 00 00 00       DCQ sub_8B64
.data.rel.ro:0000000000024450 82 BD 01 00 00 00 00 00       DCQ aAv                                 ; "av"
.data.rel.ro:0000000000024458 D0 BC 01 00 00 00 00 00       DCQ aLjavaLangStrin                     ; "()Ljava/lang/String;",0
.data.rel.ro:0000000000024460 00 8D 00 00 00 00 00 00       DCQ sub_8D00
.data.rel.ro:0000000000024468 85 BD 01 00 00 00 00 00       DCQ aSn                                 ; "sn"
.data.rel.ro:0000000000024470 88 BD 01 00 00 00 00 00       DCQ aBiLjavaLangStr                     ; "([BI)Ljava/lang/String;",0
.data.rel.ro:0000000000024478 C8 8D 00 00 00 00 00 00       DCQ sub_8DC8
.data.rel.ro:0000000000024480 A0 BD 01 00 00 00 00 00       DCQ aUrk                                ; "urk"
.data.rel.ro:0000000000024488 D0 BC 01 00 00 00 00 00       DCQ aLjavaLangStrin                     ; "()Ljava/lang/String;",0
.data.rel.ro:0000000000024490 64 8D 00 00 00 00 00 00       DCQ sub_8D64
.data.rel.ro:0000000000024498 A4 BD 01 00 00 00 00 00       DCQ aLk                                 ; "lk"
.data.rel.ro:00000000000244A0 A7 BD 01 00 00 00 00 00       DCQ aBiB                                ; "([BI)[B",0
.data.rel.ro:00000000000244A8 84 8E 00 00 00 00 00 00       DCQ sub_8E84
.data.rel.ro:00000000000244B0 AF BD 01 00 00 00 00 00       DCQ aEts                                ; "ets"
.data.rel.ro:00000000000244B8 B3 BD 01 00 00 00 00 00       DCQ aZJ                                 ; "(Z)J",0
.data.rel.ro:00000000000244C0 44 8F 00 00 00 00 00 00       DCQ sub_8F44
.data.rel.ro:00000000000244C8 B8 BD 01 00 00 00 00 00       DCQ aUksf                               ; "uksf"
.data.rel.ro:00000000000244D0 BD BD 01 00 00 00 00 00       DCQ aBiBiBLcomYuewe                     ; "([BI[BI[B)Lcom/yuewen/fock/Fock",0x24,"FockResult;",0
.data.rel.ro:00000000000244D8 50 8F 00 00 00 00 00 00       DCQ sub_8F50
.data.rel.ro:00000000000244E0 E9 BD 01 00 00 00 00 00       DCQ aResf                               ; "resf"
.data.rel.ro:00000000000244E8 EE BD 01 00 00 00 00 00       DCQ aBiBB                               ; "([BI[B)[B",0
.data.rel.ro:00000000000244F0 0C 91 00 00 00 00 00 00       DCQ sub_910C
.data.rel.ro:00000000000244F8 F8 BD 01 00 00 00 00 00       DCQ aTsf                                ; "tsf"
.data.rel.ro:0000000000024500 EE BD 01 00 00 00 00 00       DCQ aBiBB                               ; "([BI[B)[B",0
.data.rel.ro:0000000000024508 C4 91 00 00 00 00 00 00       DCQ sub_91C4
.data.rel.ro:0000000000024510 FC BD 01 00 00 00 00 00       DCQ aRmdk                               ; "rmdk"
.data.rel.ro:0000000000024518 01 BE 01 00 00 00 00 00       DCQ aBV                                 ; "([B)V",0
.data.rel.ro:0000000000024520 7C 92 00 00 00 00 00 00       DCQ sub_927C
.data.rel.ro:0000000000024528 07 BE 01 00 00 00 00 00       DCQ aIde                                ; "ide"
.data.rel.ro:0000000000024530 0B BE 01 00 00 00 00 00       DCQ aJLjavaLangStri                     ; "(J)Ljava/lang/String;",0
.data.rel.ro:0000000000024538 A8 92 00 00 00 00 00 00       DCQ sub_92A8
```

### Java Type to JNI Signature Mapping Rules:

| Java Type  | JNI Signature                  |
| ---------- | ------------------------------ |
| `int`      | `I`                            |
| `boolean`  | `Z`                            |
| `byte`     | `B`                            |
| `short`    | `S`                            |
| `long`     | `J`                            |
| `float`    | `F`                            |
| `double`   | `D`                            |
| `char`     | `C`                            |
| `void`     | `V`                            |
| `Object`   | `Lfully/qualified/ClassName;`  |
| `byte[]`   | `[B`                           |
| `int[]`    | `[I`                           |
| `Object[]` | `[Lfully/qualified/ClassName;` |

</details>

Even though it may not be strictly necessary, I decided to walk through and analyze each step out of curiosity.

---

### 1. Retrieve `JNIEnv` pointer

```c
if ( (*vm)->GetEnv(vm, (void **)&v7, 65542LL) )
    return -1;
```

* This step calls `vm->GetEnv`, storing the `JNIEnv*` into `v7` for use in subsequent JNI calls.
* If it fails, `-1` is returned, preventing the JNI library from loading.

---

### 2. Prepare a 20-byte key array `v9`

```c
v4 = 0;
memset(v9, 0, 21);
do {
    dest[0] = xmmword_1BD00;
    *((_BYTE *)v9 + v4) = *(_BYTE *)((unsigned __int64)dest | v4 & 0xF) ^ byte_1BE21[v4];
    ++v4;
} while ( v4 != 20 );
```

* `xmmword_1BD00` is a 16-byte constant, and `byte_1BE21` is a static array of at least 20 bytes.
* The XOR operation is performed byte-by-byte.
* For indices >= 16, `index & 0xF` wraps around to reuse the 16-byte constant.
* The resulting 20-byte obfuscated string is stored in `v9`.

> Below is a Python snippet that reconstructs the content of `v9`:

```python
xmmword = [
    0x76, 0x36, 0x31, 0x6F, 0x75, 0x61, 0x6B, 0x70,
    0x67, 0x34, 0x69, 0x7A, 0x6D, 0x35, 0x32, 0x77,
]
byte_1BE21 = [
    0x15, 0x59, 0x5C, 0x40, 0x0C,
    0x14, 0x0E, 0x07, 0x02, 0x5A,
    0x46, 0x1C, 0x02, 0x56, 0x59,
    0x58, 0x30, 0x59, 0x52, 0x04,
]

v9 = []
for i in range(20):
    base = xmmword[i] if i < 16 else xmmword[i & 0xF]
    v9.append(base ^ byte_1BE21[i])

ascii_vals = ''.join(chr(b) if 32 <= b < 127 else f"\\x{b:02x}" for b in v9)
print("v9 (ASCII):", ascii_vals)
"""
v9 (ASCII): com/yuewen/fock/Fock
"""
```

---

### 3. Create `byte[]` or look up the class (depends on actual offset)

```c
v5 = (*(__int64 (__fastcall **)(__int64, __int64 *, long double))(*(_QWORD *)v7 + 48LL))(
       v7,
       v9,
       *(long double *)&xmmword_1BD00);
if ( !v5 )
    return -1;
v6 = v5;
```

* Calls the function at offset `+48` of the `JNIEnv` vtable (likely `NewByteArray`, `FindClass`, or a hooked method).
* Parameters passed: the `v9` byte array and `xmmword_1BD00` (treated as a `long double`).
* The return value (e.g., a `jbyteArray` or `jclass`) is stored in `v6`.

---

### 4. Register the native method table

```c
memcpy(dest, off_24408, 0x138u);
if ((*(unsigned int (__fastcall **)(__int64, __int64, __int128 *, __int64))(*(_QWORD *)v7 + 1720LL))(
       v7,
       v6,
       dest,
       13LL))
{
    return -1;
}
```

* `off_24408` holds a contiguous block of 13 `JNINativeMethod` structs (13×24 = 312 bytes = 0x138).
* The function at offset `+1720` in the vtable (i.e., `RegisterNatives`) is called.
* The methods are registered to the class reference stored in `v6`.

---

### 3.5.4 Bulk Decryption and Export

Combining all the modules mentioned above, we can construct a complete batch decryption script.

This script processes all `.qd` files under a given directory and exports each decrypted result as a `.json` file for further analysis or use.

**Before running**, make sure to edit the parameters in the `main()` function as needed:

* `book_id`, `user_id`, `imei` (used in decryption)
* `device = frida.get_device("your.device.ip.address")` (adjust for IP or USB as appropriate)

**Default behavior:**

* Input directory: `./data/{book_id}/` (containing chapter `.qd` files)
* Output directory: `./output/{book_id}/` (exports decrypted `.json` files)

<details>
<summary>`qd_decrypt.py` (click to expand)</summary>

```python
import json
import hashlib
import hmac
from base64 import b64encode
from io import BytesIO
from pathlib import Path
from typing import Any

import frida
from Crypto.Cipher import DES3
from Crypto.Util.Padding import unpad


def sha1_hmac(key: str, data: str) -> str:
    digest = hmac.new(key.encode(), data.encode(), hashlib.sha1).digest()
    return b64encode(digest).decode()[:24]


def md5_hmac(key: str, data: str) -> str:
    digest = hmac.new(key.encode(), data.encode(), hashlib.md5).digest()
    return b64encode(digest).decode()[:24]


def des3_decrypt(data: bytes, secret: str) -> bytes:
    """3DES/CBC decryption"""
    cipher = DES3.new(secret.encode(), DES3.MODE_CBC, b'\x00' * 8)
    decrypted = cipher.decrypt(data)
    return unpad(decrypted, block_size=8)


def decrypt_content(cid: str, chunk1: bytes, uid: str, imei: str) -> str:
    """
    - Perform double 3DES decryption on chunk1
    - Automatically detect and remove PKCS#7 padding
    - Remove trailing non-encrypted 'extra' bytes
    """
    sec1 = sha1_hmac(
        imei,
        uid + imei + cid + "2EEE1433A152E84B3756301D8FA3E69A",
    )
    sec2 = md5_hmac(uid, sec1 + imei)

    raw = chunk1
    step1 = des3_decrypt(raw, sec2)
    step2 = des3_decrypt(step1, sec1)

    return step2.decode("utf-8", errors="ignore")


def decrypt(
    path: Path,
    book_id: str,
    uid: str,
    imei: str,
    script,
) -> dict[str, Any]:
    """
    Decrypt a Qidian chapter '.qd' file

    The file format corresponds to the structure defined in Java method `com.qidian.common.lib.util.m.r`:

    Uses fixed-length prefix structure `[len0][data0][len1][data1]...[len4][data4]`, total 5 segments.

    Summary of the decryption process:
    - Read encrypted data chunks sequentially
    - Decrypt using the algorithm and Frida-provided JS script
    - If `type == 1`, further unpack content and block structure info
    """
    cid = path.stem
    with path.open('rb') as f:
        buf = BytesIO(f.read())

    def decode_str(barr: bytes) -> str:
        try:
            return barr.decode('utf-8')
        except Exception:
            return barr.decode('utf-8', errors='replace')

    def read_chunk():
        raw = buf.read(4)
        if len(raw) < 4:
            raise IOError("Incomplete file structure, unable to read length")
        length = int.from_bytes(raw, byteorder='little')
        return buf.read(length)

    # Sequentially read all 5 chunks
    chunk0 = read_chunk()
    chunk1 = read_chunk()
    chunk2 = read_chunk()
    chunk3 = read_chunk()
    chunk4 = read_chunk()

    text_1 = decrypt_content(cid, chunk1, uid, imei)
    content = ""
    content_type = 0
    block_infos = []
    author_content = {}
    resources = []
    try:
        data_obj = json.loads(text_1 or "{}")
        content = data_obj.get("content") or data_obj.get("Content", "")
        content_type = data_obj.get("type", 0)
        block_infos = data_obj.get("Blocks", [])
        author_content = data_obj.get("AuthorComments", {})
        resources = data_obj.get("Resources", [])
    except Exception as e:
        print(f"decrypt_content(cid = {cid}): {e}")

    if content_type == 1:
        key_1 = cid
        key_2 = f"{book_id}_{cid}"
        raw = script.exports_sync.unlock(content, key_1, key_2)
        if raw:
            try:
                decoded = json.loads(raw)
                content = decoded.get("content", "")
            except Exception:
                pass

        try:
            txt2 = decode_str(chunk2)
            author_content = json.loads(txt2)
        except Exception:
            author_content = {}

        block_infos: list[Any] = []
        try:
            txt4 = decode_str(chunk4)
            if txt4:
                block_infos = json.loads(txt4)
        except Exception:
            block_infos = []

    return {
        "content": content,
        "type": content_type,
        "author_comments": author_content,
        "blocks": block_infos,
        "resources": resources,
    }


def main():
    book_id = "11111111"
    user_id = "22222222"
    imei = "your:imei:info"

    data_dir = Path.cwd() / "data" / book_id
    out_dir = Path.cwd() / "output" / book_id
    out_dir.mkdir(parents=True, exist_ok=True)

    device = frida.get_device("your.device.ip.address")

    session = device.attach("起点读书")

    with open("hook_fock.js", "r", encoding="utf-8") as f:
        jscode = f.read()

    script = session.create_script(jscode)
    script.load()

    print("[*] Script loaded. Starting unlock tasks...")

    for file_path in data_dir.glob("*.qd"):
        cid = file_path.stem
        out_path = out_dir / f"{cid}.json"

        try:
            obj = decrypt(
                file_path,
                book_id,
                user_id,
                imei,
                script,
            )
        except Exception as e:
          obj = {"error": str(e)}

        with out_path.open('w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)

        print(f"{file_path.name} -> {out_path.name}")


if __name__ == "__main__":
    main()
```
</details>
