private rule upx
{
    meta:
        _description = "Binary signature for UPX-packed executable(s)."
        _author = "Jason Batchelor"
        _date = "2014-12-17 00:00:00"

        _trigger = "unpack.upx"

    strings:
        $mz = "MZ"
        $upx1 = { 55 50 58 30 00 00 00 }
        $upx2 = { 55 50 58 31 00 00 00 }
        $upx_sig = "UPX!"

    condition:
        $mz at 0 and $upx1 in (0..1024) and $upx2 in (0..1024) and $upx_sig in (0..1024)
}
