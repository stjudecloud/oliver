workflow hello_workflow {
    call hello_task
}

task hello_task {
    command {
        echo "Hello, Oliver!"
    }
    output {
        String out = read_string(stdout())
    }
}