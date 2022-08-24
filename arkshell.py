import sys
import ark as lang

# try:
while True:
    enter = input("vshell $ ")
    if enter == "quit":
        sys.exit(0)

    result, error = lang.run("shell.vam", enter)
    if error :
        print(error)
    else:
        print(result.value)

            
# except Exception as e:
#     print("Compilation failed:", e)
#     sys.exit(0)
# except
# except:
#     print("Compilation failed due to unknown error")
#     sys.exit(0)
