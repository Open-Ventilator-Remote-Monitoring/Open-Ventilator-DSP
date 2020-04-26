

def main():
    string = ""
    num_lines = 0
    with open("../data/matlab_output.txt", 'r') as f:
        lines = f.readlines()
        num_lines = len(lines)
        for line in lines:
            string = "{}{}".format(string, line)

    prefix = ""
    if "LOW" in string:
        prefix = "lpf"
    elif "HIGH" in string:
        prefix = "hpf"
    elif "BANDPASS":
        prefix = "bpf"

    string = string.replace("}", "]")
    string = string.replace("{", "[")
    string = string.replace("[]", "")
    string = string.replace(";", "")
    string = string.replace("GAIN", "g")
    string = string.replace("G", "g")
    string = string.replace("//", "#")
    string = string.replace("static float ", "")
    string = string.replace("const int ", "")

    if "lpf" == prefix:
        string = string.replace("a", "lpfa")
        string = string.replace("b", "lpfb")
        string = string.replace("g", "lpfg")
    elif "hpf" == prefix:
        string = string.replace("a", "hpfa")
        string = string.replace("b", "hpfb")
        string = string.replace("g", "hpfg")
    elif "bpf" == prefix:
        string = string.replace("a", "bpfa")
        string = string.replace("b", "bpfb")
        string = string.replace("g", "bpfg")

    string = "{}\n{} = [".format(string, prefix)

    for i in range((num_lines-1)//3):
        string = "{string}[{prefix}g{i}, {prefix}a{i}, {prefix}b{i}],".format(prefix=prefix, string=string, i=i+1)

    string = "{}]".format(string)
    with open("../data/matlab_formatted_output.txt", 'w') as f:
        f.write(string)






if __name__ == "__main__":
    main()