rule Hello
{
    strings:
        $hello = "hello"

    condition:
        $hello
}
