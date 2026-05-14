# Burp Extensions

A collection of Burp Suite extensions developed for offensive security engagements where the off-the-shelf tooling falls short. Each extension lives in its own directory with a dedicated README covering setup and usage.

## Extensions

| Extension | Path | Purpose |
| --- | --- | --- |
| Mainframe EBCDIC Editor (`EBCDitor`) | [Mainframe_EBCDIC_Editor/](Mainframe_EBCDIC_Editor/) | Decode, edit, and re-encode EBCDIC-encoded payloads inside Burp Repeater / Proxy when pentesting IBM mainframe applications over TN3270 or HTTP-wrapped streams. |

## Requirements

These extensions are written in **Jython** and target the Burp Suite Extender API.

- Burp Suite Community or Professional (1.7 or later)
- Jython 2.7 standalone JAR ([download](https://www.jython.org/download))
- Java 11+ (bundled with modern Burp installations)

## Installing a Jython extension in Burp

1. **Burp Suite -> Settings -> Extensions -> Jython environment**: select the path to `jython-standalone-2.7.x.jar`.
2. **Extensions -> Installed -> Add**:
   - **Extension type:** `Python`
   - **Extension file:** path to the `.py` file (for example `Mainframe_EBCDIC_Editor/EBCDitor.py`)
3. Confirm the extension name and version appear under **Installed** with no errors in the **Output** / **Errors** tabs.

## Repository layout

```
Burp_Extentions/
|-- README.md                          # this file
`-- Mainframe_EBCDIC_Editor/
    |-- README.md                      # extension-specific docs
    `-- EBCDitor.py                    # the extension source
```

## Author

[@redroot97](https://github.com/redroot97) - offensive security engineer.
Issues and pull requests welcome.

## License

Released under the MIT License unless stated otherwise inside an extension directory.
