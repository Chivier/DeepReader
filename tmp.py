# Raw cookie string (replace with your full cookie string)
raw_cookies = """
buvid3=C4E9956D-F86E-888B-A338-AA54CD05621161447infoc; b_nut=1722605561; _uuid=B6D1D81A-55AF-9614-3B36-7AF1D81087BA358373infoc; enable_web_push=DISABLE; ...
"""

# Domain for the cookies
domain = ".bilibili.com"

# Output file
output_file = "cookie.txt"

# Convert raw cookies to Netscape format
with open(output_file, "w") as f:
    f.write("# Netscape HTTP Cookie File\n")
    f.write("# This file is generated automatically.\n\n")
    
    cookies = raw_cookies.strip().split("; ")
    for cookie in cookies:
        name, value = cookie.split("=", 1)
        f.write(f"{domain}\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")

print(f"Cookies saved to {output_file}")

