import sys
import vampire as lang

def readFile(filename):
    with open(filename, "r") as io:
        text = io.read()
    return text

def writeFile(filename, text):
    with open(filename, "w", encoding="utf-8") as io:
        io.write(text)
def run():
    filename = sys.argv[1]
    fileext = ".my"
    outfile = filename.replace(fileext, ".py")
    text = readFile(filename)
    result, error = lang.run(filename, text)
    if error :
        print("Compilation failed:\a")
        print("")
        print(error)
    else:
        writeFile(outfile, result.statements)
# try:
if len(sys.argv) > 1:
    if len(sys.argv) == 2 : run()

            
# except Exception as e:
#     print("Compilation failed:", e)
#     sys.exit(0)
# except
# except:
#     print("Compilation failed due to unknown error")
#     sys.exit(0)