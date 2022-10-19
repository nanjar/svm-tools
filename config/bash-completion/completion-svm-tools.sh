#/usr/bin/env bash
complete -W "production rabbit-consumer veritrans controller virtual-tty svm-scheduled-restart ui" svm-tail-log
complete -W "--reboot --get" svm-cmd-router

