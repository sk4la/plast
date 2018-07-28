private rule zip
{
    meta:
        _description = "Binary signature for ZIP archive(s)."
        _author = "Jason Batchelor"
        _date = "2014-12-17 00:00:00"

        _trigger = "inflate.zip"

    strings:
        $magic = { 50 4B 03 04 }

    condition:
        $magic at 0
}

private rule jar
{
    meta:
        _description = "Binary signature for JAR file(s)."
        _author = "Jason Batchelor"
        _date = "2015-08-10 00:00:00"

        _trigger = "inflate.jar"

    strings:
        $magic = { 50 4B 03 04 }
        $manifest = "META-INF/MANIFEST.MF"

   condition:
      $magic at 0 and $manifest
}

private rule tar
{
    meta:
        _description = "Binary signature for TAR archive(s)."
        _author = "Jason Batchelor"
        _date = "2015-11-16 00:00:00"

        _trigger = "inflate.tar"

    strings:
        $magic = { 75 73 74 61 72 }

    condition:
        $magic at 257
}

private rule rar
{
    meta:
        _description = "Binary signature for RAR archive(s)."
        _author = "James Ferrer"
        _date = "2015-01-07 00:00:00"

        _trigger = "inflate.rar"

    strings:
        $magic = { 52 61 72 21 1A 07 }

    condition:
        $magic at 0
}

private rule gzip
{
    meta:
        _description = "Binary signature for GZIP archive(s)."
        _author = "Jason Batchelor"
        _date = "2015-11-16 00:00:00"

        _trigger = "inflate.gzip"

    strings:
        $magic = { 1F 8B 08 }

    condition:
        $magic at 0
}

private rule 7z
{
    meta:
        _description = "Binary signature for 7-Zip archive(s)."
        _author = "Jaume Martin"
        _date = "2018-07-27 18:08:00"

        _trigger = "inflate.7z"

    strings:
        $magic = { 37 7A BC AF 27 1C }

    condition:
        $magic at 0
}
