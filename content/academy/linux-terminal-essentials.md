---
{
  "title": "Linux Terminal Essentials for Beginners",
  "articleType": "tutorial",
  "author": "StackedByBayo",
  "evergreen": true,
  "learningLevel": "beginner",
  "category": "Linux",
  "categories": ["linux"],
  "excerpt": "Learn to navigate directories, read files and combine commands in a practice folder you can safely make yourself.",
  "sources": [
    {"label": "Ubuntu’s beginner guide to the Linux command line", "url": "https://documentation.ubuntu.com/desktop/en/26.04/tutorial/the-linux-command-line-for-beginners/"}
  ]
}
---

The terminal is a way to give your computer instructions in text. You only need a few commands to get oriented, read a file and find a line of interest. Practise those first and unfamiliar examples become easier to read.

## What you’ll learn

You’ll find your current directory, work with absolute and relative paths, and send one command’s output into another.

## Prerequisites

You’ll need a Linux shell, such as the one in Ubuntu’s Terminal app. Use an ordinary user account. The examples create a temporary practice directory and files inside it.

## Understand the prompt and your location

The terminal displays a prompt from a program called a shell. The shell reads your input and decides which command to run. A command can take options and arguments. In `ls -l notes.txt`, `ls` is the command, `-l` requests a detailed listing, and `notes.txt` is the file to list.

Start with these commands:

```shell
pwd
ls
ls -la
```

`pwd` reports the current directory. `ls` lists its contents. Adding `-l` gives more detail, while `-a` includes names that start with a dot. Two common entries are `.`, the current directory, and `..`, its parent.

A path starting with `/` is absolute. It starts at the root of the filesystem. A path such as `notes.txt` or `practice/notes.txt` is relative to your current directory. The shell also expands an unquoted `~` at the start of a path to your home directory.

## Make a practice directory

```shell
practice_dir="$(mktemp -d)" && cd "$practice_dir" && pwd
```

`mktemp -d` creates a new temporary directory and prints its path. The variable `practice_dir` stores that path. Quoting the variable keeps the path together if it contains spaces. Each `&&` runs the following command only if the preceding one succeeded. Before continuing, make sure `pwd` printed the path of the newly created directory.

```shell
printf '%s\n' 'Read the notes' 'Check the logs' 'Save the results' > notes.txt
cat notes.txt
cp -i notes.txt "notes copy.txt"
ls -l
```

The `>` operator redirects the output of `printf` into `notes.txt`. It replaces the previous contents if the file already exists. `cat` prints the file, and `cp -i` prompts before overwriting a destination. In the listing, both filenames should be present. Quote `notes copy.txt` whenever you use it as one argument.

## Filter command output with a pipe

```shell
grep -n 'logs' notes.txt
grep 'logs' notes.txt | wc -l
```

The first command shows the matching line and its line number. The second uses `|` to make the output of `grep` the input of `wc`. In this example `wc -l` prints `1` because it receives one matching line. You can run each part on its own while learning what is being passed between commands.

Try searching for `'notes'` instead, then use `ls -l "notes copy.txt"` to practise quoting a filename. If a command reports that a file cannot be found, run `pwd` and `ls` before changing anything. The filename might be spelled correctly but in a different directory.

## Key takeaways

Use `pwd` to establish where you are. Quote filenames with spaces. Read the destination before running a command that writes or overwrites a file.

## Suggested next reading

See [how these habits apply to Linux troubleshooting](../../blog/troubleshooting-the-problems-that-actually-taught-me-linux/).
