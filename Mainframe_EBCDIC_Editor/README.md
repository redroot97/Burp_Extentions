# Mainframe EBCDIC Editor (EBCDitor)

A Burp Suite extension that decodes, edits, and re-encodes **EBCDIC**-formatted payloads in-place, written for pentesting IBM mainframe applications that speak EBCDIC (typically over **TN3270** or HTTP-wrapped streams via NoPE Proxy or similar bridges).

Burp's built-in decoders do not understand EBCDIC. When a thick client talks to an IBM 3278-2 / 3279 terminal over TN3270, the bytes you see in Burp's request view are unreadable garbage. **EBCDitor** sits inside Burp and lets you select a region of the raw frame, view it as readable ASCII, modify the values, and produce the re-encoded EBCDIC bytes you can drop back into the request.

---

## Features

- One-click context-menu entry inside any Burp message editor (Proxy, Repeater, Intruder, History).
- Decode highlighted bytes from EBCDIC (IBM code page **`cp500`**) to readable ASCII.
- Edit the decoded text in a resizable Swing text area.
- Re-encode the edited text back to EBCDIC bytes ready to paste into Burp.
- Preserves the last two bytes of the selection (commonly TN3270 frame terminators / control bytes) so the protocol structure is not broken.
- No external dependencies beyond Burp + Jython.

---

## How it works

1. The extension registers a context-menu factory with Burp via the Extender API.
2. When **Edit** is invoked on a selection, the extension:
   1. Reads the raw bytes of the highlighted region.
   2. Slices off the last two bytes (typical TN3270 control terminators) and keeps them aside.
   3. Decodes the remaining bytes with `cp500` (EBCDIC International, the codec used by most z/OS systems) to get ASCII text.
   4. Shows the ASCII text in an editable dialog.
   5. On **OK**: encodes the user's edits back to `cp500`, appends the stored trailing bytes, and presents the resulting raw byte string in a second dialog for copy-paste back into Burp.

> The extension does **not** mutate the message in Burp automatically. It produces the re-encoded bytes for you to paste into the request. This is intentional - it keeps you in control of where exactly the payload lands in the frame.

---

## Requirements

| Component | Version |
| --- | --- |
| Burp Suite (Community or Professional) | 1.7 or later |
| Jython standalone JAR | 2.7.x ([download](https://www.jython.org/download)) |
| Java runtime | 11+ (bundled with modern Burp) |

If you also need to proxy raw TN3270 traffic through Burp, install [NoPE Proxy](https://github.com/summitt/Burp-Non-HTTP-Extension) (or an equivalent non-HTTP proxy extension) and configure your terminal emulator to use it.

---

## Setup

1. **Configure Jython in Burp**
   - Burp Suite -> **Settings** -> **Extensions** -> **Jython environment**.
   - Point **Location of Jython standalone JAR** at the downloaded `jython-standalone-2.7.x.jar`.
2. **Load EBCDitor**
   - **Extensions** -> **Installed** -> **Add**.
   - **Extension type:** `Python`.
   - **Extension file:** path to `Mainframe_EBCDIC_Editor/EBCDitor.py`.
   - Click **Next**. You should see `EBCDIC to ASCII Converter extension loaded` in the output tab and `EBCDIC Editor` listed under **Installed**.
3. *(Optional)* If you are working with TN3270 streams, wire up NoPE Proxy so the raw mainframe traffic shows up in Burp Proxy / Repeater.

---

## Usage

1. Open any Burp tab that lets you select bytes (Repeater is easiest).
2. In the **Request** or **Response** view, highlight the bytes you want to decode.
   - Select only the EBCDIC payload region. Leave protocol headers, length prefixes, and AID bytes outside the selection unless you intend to edit them.
3. Right-click the selection -> **Extensions** -> **EBCDIC Editor** -> **Edit**.
4. A dialog titled **EBCDIC -> ASCII** appears with the decoded ASCII text. Edit it as needed.
5. Click **OK**. A second dialog titled **ASCII -> EBCDIC** shows the re-encoded raw byte string (with the original trailing two bytes preserved).
6. Copy the contents of that dialog and paste them back over the original selection in Burp. Send the request.

---

## Example

### Captured TN3270 frame (Burp Repeater, raw view)

```
00000000  05 c3 11 40 40 13 c5 d5  e3 c5 d9 40 e4 e2 c5 d9   ...@@.E NTER USER
00000010  c9 c4 6b 40 d7 c1 e2 e2  e6 d6 d9 c4 11 40 40 13   ID, PASSWORD .@@.
00000020  c1 c4 d4 c9 d5 11 40 40  13 d7 81 a2 a2 e6 6e f0   ADMIN .@@.Passw=0
00000030  f0 f9 ff ef                                        09..
```

### Step 1 - select the EBCDIC region

Highlight bytes `0x06` through `0x33` (the printable EBCDIC content, leaving the leading TN3270 header bytes alone).

### Step 2 - run EBCDitor

Right-click -> **Extensions** -> **EBCDIC Editor** -> **Edit**. The dialog shows:

```
ENTER USERID, PASSWORD
ADMIN
Passw=00909
```

### Step 3 - edit the decoded text

Change the credential and submit something more interesting:

```
ENTER USERID, PASSWORD
ADMIN
Passw=' OR 1=1 --
```

### Step 4 - re-encoded EBCDIC output

Click **OK**. EBCDitor presents the byte string ready to paste back over the original selection:

```
ENTER USERID, PASSWORD\nADMIN\nPassw='\x7d OR 1\x7e1 --[CR][LF]
```

(Shown with the trailing two bytes preserved so the TN3270 frame still parses on the wire.)

Paste it into Burp, send the request, and observe the mainframe's response.

---

## Code paths

| Function | Responsibility |
| --- | --- |
| `registerExtenderCallbacks` | Names the extension and registers the context-menu factory. |
| `createMenuItems` | Adds the `Edit` action to the right-click menu when a selection exists. |
| `convertEBCDICToASCII` | Reads selection bytes, peels off the trailing two bytes, decodes `cp500`, prompts the user, then re-encodes and shows the resulting bytes. |

The `cp500` codec is hard-coded because most z/OS deployments default to **EBCDIC International (IBM-500)**. If you are working with a code page that differs (for example `cp1047`, `cp037`, `cp273` for German), edit the `encode('cp500')` / `decode('cp500')` calls in [EBCDitor.py](EBCDitor.py).

---

## Limitations and notes

- The extension does **not** auto-replace the original bytes in the Burp message. By design - it shows you the new payload so you decide exactly where it goes.
- Hard-coded to `cp500`. Swap to your target's code page if needed.
- The "strip the last two bytes" behavior assumes a TN3270-style trailer. If you're pasting EBCDIC payloads from a different transport, you may want to comment out that block in [EBCDitor.py](EBCDitor.py).
- Errors during encode / decode are caught and surfaced via `callbacks.issueAlert(...)` and the extension's output tab.

---

## Troubleshooting

- **Nothing happens when I click Edit.** Make sure you have an actual byte selection in the message editor. The menu item is enabled only when a selection exists.
- **`UnicodeDecodeError` or garbled output.** The bytes selected are probably not `cp500`. Try a different EBCDIC code page (see above) or narrow the selection to only the payload region.
- **`EBCDIC to ASCII Converter extension loaded` does not appear.** Confirm the Jython standalone JAR is configured and that the extension loaded without errors in the **Errors** tab.

---

## Author

Built by [@redroot97](https://github.com/redroot97) during enterprise red team and mainframe pentesting engagements where every other EBCDIC editor required tabbing out of Burp.

Issues and PRs welcome on the parent repository.
