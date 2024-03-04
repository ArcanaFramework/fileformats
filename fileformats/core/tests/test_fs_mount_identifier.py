import os.path
import platform
import pytest
from fileformats.core.fs_mount_identifier import FsMountIdentifier
from fileformats.generic import File


MOUNT_OUTPUTS = (
    # Linux, no CIFS
    (
        r"""sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime)
proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
udev on /dev type devtmpfs (rw,nosuid,relatime,size=8121732k,nr_inodes=2030433,mode=755)
devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000)
tmpfs on /run type tmpfs (rw,nosuid,noexec,relatime,size=1628440k,mode=755)
/dev/nvme0n1p2 on / type ext4 (rw,relatime,errors=remount-ro,data=ordered)
securityfs on /sys/kernel/security type securityfs (rw,nosuid,nodev,noexec,relatime)
tmpfs on /dev/shm type tmpfs (rw,nosuid,nodev)
tmpfs on /sys/fs/cgroup type tmpfs (ro,nosuid,nodev,noexec,mode=755)
cgroup on /sys/fs/cgroup/systemd type cgroup (rw,nosuid,nodev,noexec,relatime,xattr,release_agent=/lib/systemd/systemd-cgroups-agent,name=systemd)
pstore on /sys/fs/pstore type pstore (rw,nosuid,nodev,noexec,relatime)
efivarfs on /sys/firmware/efi/efivars type efivarfs (rw,nosuid,nodev,noexec,relatime)
cgroup on /sys/fs/cgroup/cpu,cpuacct type cgroup (rw,nosuid,nodev,noexec,relatime,cpu,cpuacct)
cgroup on /sys/fs/cgroup/freezer type cgroup (rw,nosuid,nodev,noexec,relatime,freezer)
cgroup on /sys/fs/cgroup/pids type cgroup (rw,nosuid,nodev,noexec,relatime,pids)
cgroup on /sys/fs/cgroup/cpuset type cgroup (rw,nosuid,nodev,noexec,relatime,cpuset)
systemd-1 on /proc/sys/fs/binfmt_misc type autofs (rw,relatime,fd=26,pgrp=1,timeout=0,minproto=5,maxproto=5,direct)
hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime)
debugfs on /sys/kernel/debug type debugfs (rw,relatime)
mqueue on /dev/mqueue type mqueue (rw,relatime)
fusectl on /sys/fs/fuse/connections type fusectl (rw,relatime)
/dev/nvme0n1p1 on /boot/efi type vfat (rw,relatime,fmask=0077,dmask=0077,codepage=437,iocharset=iso8859-1,shortname=mixed,errors=remount-ro)
/dev/nvme0n1p2 on /var/lib/docker/aufs type ext4 (rw,relatime,errors=remount-ro,data=ordered)
gvfsd-fuse on /run/user/1002/gvfs type fuse.gvfsd-fuse (rw,nosuid,nodev,relatime,user_id=1002,group_id=1002)
""",
        0,
        [
            ("/sys/fs/cgroup/cpu,cpuacct", "cgroup"),
            ("/sys/firmware/efi/efivars", "efivarfs"),
            ("/proc/sys/fs/binfmt_misc", "autofs"),
            ("/sys/fs/fuse/connections", "fusectl"),
            ("/sys/fs/cgroup/systemd", "cgroup"),
            ("/sys/fs/cgroup/freezer", "cgroup"),
            ("/sys/fs/cgroup/cpuset", "cgroup"),
            ("/sys/kernel/security", "securityfs"),
            ("/var/lib/docker/aufs", "ext4"),
            ("/sys/fs/cgroup/pids", "cgroup"),
            ("/run/user/1002/gvfs", "fuse.gvfsd-fuse"),
            ("/sys/kernel/debug", "debugfs"),
            ("/sys/fs/cgroup", "tmpfs"),
            ("/sys/fs/pstore", "pstore"),
            ("/dev/hugepages", "hugetlbfs"),
            ("/dev/mqueue", "mqueue"),
            ("/boot/efi", "vfat"),
            ("/dev/pts", "devpts"),
            ("/dev/shm", "tmpfs"),
            ("/proc", "proc"),
            ("/sys", "sysfs"),
            ("/dev", "devtmpfs"),
            ("/run", "tmpfs"),
            ("/", "ext4"),
        ],
    ),
    # OS X, no CIFS
    (
        r"""/dev/disk2 on / (hfs, local, journaled)
devfs on /dev (devfs, local, nobrowse)
map -hosts on /net (autofs, nosuid, automounted, nobrowse)
map auto_home on /home (autofs, automounted, nobrowse)
map -fstab on /Network/Servers (autofs, automounted, nobrowse)
/dev/disk3s2 on /Volumes/MyBookData (hfs, local, nodev, nosuid, journaled)
afni:/elrond0 on /Volumes/afni (nfs)
afni:/var/www/INCOMING on /Volumes/INCOMING (nfs)
afni:/fraid on /Volumes/afni (nfs, asynchronous)
boromir:/raid.bot on /Volumes/raid.bot (nfs)
elros:/volume2/AFNI_SHARE on /Volumes/AFNI_SHARE (nfs)
map -static on /Volumes/safni (autofs, automounted, nobrowse)
map -static on /Volumes/raid.top (autofs, automounted, nobrowse)
/dev/disk1s3 on /Volumes/Boot OS X (hfs, local, journaled, nobrowse)
""",
        0,
        [
            ("/Volumes/MyBookData", "hfs"),
            ("/Volumes/AFNI_SHARE", "nfs"),
            ("/Volumes/Boot OS X", "hfs"),
            ("/Volumes/INCOMING", "nfs"),
            ("/Volumes/raid.bot", "nfs"),
            ("/Volumes/raid.top", "autofs"),
            ("/Network/Servers", "autofs"),
            ("/Volumes/safni", "autofs"),
            ("/Volumes/afni", "nfs"),
            ("/Volumes/afni", "nfs"),
            ("/home", "autofs"),
            ("/dev", "devfs"),
            ("/net", "autofs"),
            ("/", "hfs"),
        ],
    ),
    # Non-zero exit code
    ("", 1, []),
    # Variant of Linux example with CIFS added manually
    (
        r"""sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime)
proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
udev on /dev type devtmpfs (rw,nosuid,relatime,size=8121732k,nr_inodes=2030433,mode=755)
devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000)
tmpfs on /run type tmpfs (rw,nosuid,noexec,relatime,size=1628440k,mode=755)
/dev/nvme0n1p2 on / type ext4 (rw,relatime,errors=remount-ro,data=ordered)
securityfs on /sys/kernel/security type securityfs (rw,nosuid,nodev,noexec,relatime)
tmpfs on /dev/shm type tmpfs (rw,nosuid,nodev)
tmpfs on /sys/fs/cgroup type tmpfs (ro,nosuid,nodev,noexec,mode=755)
cgroup on /sys/fs/cgroup/systemd type cgroup (rw,nosuid,nodev,noexec,relatime,xattr,release_agent=/lib/systemd/systemd-cgroups-agent,name=systemd)
pstore on /sys/fs/pstore type pstore (rw,nosuid,nodev,noexec,relatime)
efivarfs on /sys/firmware/efi/efivars type efivarfs (rw,nosuid,nodev,noexec,relatime)
cgroup on /sys/fs/cgroup/cpu,cpuacct type cgroup (rw,nosuid,nodev,noexec,relatime,cpu,cpuacct)
cgroup on /sys/fs/cgroup/freezer type cgroup (rw,nosuid,nodev,noexec,relatime,freezer)
cgroup on /sys/fs/cgroup/pids type cgroup (rw,nosuid,nodev,noexec,relatime,pids)
cgroup on /sys/fs/cgroup/cpuset type cgroup (rw,nosuid,nodev,noexec,relatime,cpuset)
systemd-1 on /proc/sys/fs/binfmt_misc type autofs (rw,relatime,fd=26,pgrp=1,timeout=0,minproto=5,maxproto=5,direct)
hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime)
debugfs on /sys/kernel/debug type debugfs (rw,relatime)
mqueue on /dev/mqueue type mqueue (rw,relatime)
fusectl on /sys/fs/fuse/connections type fusectl (rw,relatime)
/dev/nvme0n1p1 on /boot/efi type vfat (rw,relatime,fmask=0077,dmask=0077,codepage=437,iocharset=iso8859-1,shortname=mixed,errors=remount-ro)
/dev/nvme0n1p2 on /var/lib/docker/aufs type ext4 (rw,relatime,errors=remount-ro,data=ordered)
gvfsd-fuse on /run/user/1002/gvfs type fuse.gvfsd-fuse (rw,nosuid,nodev,relatime,user_id=1002,group_id=1002)
""",
        0,
        [
            ("/sys/fs/cgroup/cpu,cpuacct", "cgroup"),
            ("/sys/firmware/efi/efivars", "efivarfs"),
            ("/proc/sys/fs/binfmt_misc", "autofs"),
            ("/sys/fs/fuse/connections", "fusectl"),
            ("/sys/fs/cgroup/systemd", "cgroup"),
            ("/sys/fs/cgroup/freezer", "cgroup"),
            ("/sys/fs/cgroup/cpuset", "cgroup"),
            ("/sys/kernel/security", "securityfs"),
            ("/var/lib/docker/aufs", "ext4"),
            ("/sys/fs/cgroup/pids", "cgroup"),
            ("/run/user/1002/gvfs", "fuse.gvfsd-fuse"),
            ("/sys/kernel/debug", "debugfs"),
            ("/sys/fs/cgroup", "tmpfs"),
            ("/sys/fs/pstore", "pstore"),
            ("/dev/hugepages", "hugetlbfs"),
            ("/dev/mqueue", "mqueue"),
            ("/boot/efi", "vfat"),
            ("/dev/pts", "devpts"),
            ("/dev/shm", "tmpfs"),
            ("/proc", "proc"),
            ("/sys", "sysfs"),
            ("/dev", "devtmpfs"),
            ("/run", "tmpfs"),
            ("/", "ext4"),
        ],
    ),
    # Variant of OS X example with CIFS added manually
    (
        r"""/dev/disk2 on / (hfs, local, journaled)
devfs on /dev (devfs, local, nobrowse)
afni:/elrond0 on /Volumes/afni (cifs)
afni:/var/www/INCOMING on /Volumes/INCOMING (nfs)
afni:/fraid on /Volumes/afni/fraid (nfs, asynchronous)
boromir:/raid.bot on /Volumes/raid.bot (nfs)
elros:/volume2/AFNI_SHARE on /Volumes/AFNI_SHARE (nfs)
""",
        0,
        [
            ("/Volumes/afni/fraid", "nfs"),
            ("/Volumes/AFNI_SHARE", "nfs"),
            ("/Volumes/INCOMING", "nfs"),
            ("/Volumes/raid.bot", "nfs"),
            ("/Volumes/afni", "cifs"),
            ("/dev", "devfs"),
            ("/", "hfs"),
        ],
    ),
    # From Windows: docker run --rm -it -v C:\:/data busybox mount
    (
        r"""overlay on / type overlay (rw,relatime,lowerdir=/var/lib/docker/overlay2/l/26UTYITLF24YE7KEGTMHUNHPPG:/var/lib/docker/overlay2/l/SWGNP3T2EEB4CNBJFN3SDZLXHP,upperdir=/var/lib/docker/overlay2/a4c54ab1aa031bb5a14a424abd655510521e183ee4fa4158672e8376c89df394/diff,workdir=/var/lib/docker/overlay2/a4c54ab1aa031bb5a14a424abd655510521e183ee4fa4158672e8376c89df394/work)
proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
tmpfs on /dev type tmpfs (rw,nosuid,size=65536k,mode=755)
devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=666)
sysfs on /sys type sysfs (ro,nosuid,nodev,noexec,relatime)
tmpfs on /sys/fs/cgroup type tmpfs (ro,nosuid,nodev,noexec,relatime,mode=755)
cpuset on /sys/fs/cgroup/cpuset type cgroup (ro,nosuid,nodev,noexec,relatime,cpuset)
cpu on /sys/fs/cgroup/cpu type cgroup (ro,nosuid,nodev,noexec,relatime,cpu)
cpuacct on /sys/fs/cgroup/cpuacct type cgroup (ro,nosuid,nodev,noexec,relatime,cpuacct)
blkio on /sys/fs/cgroup/blkio type cgroup (ro,nosuid,nodev,noexec,relatime,blkio)
memory on /sys/fs/cgroup/memory type cgroup (ro,nosuid,nodev,noexec,relatime,memory)
devices on /sys/fs/cgroup/devices type cgroup (ro,nosuid,nodev,noexec,relatime,devices)
freezer on /sys/fs/cgroup/freezer type cgroup (ro,nosuid,nodev,noexec,relatime,freezer)
net_cls on /sys/fs/cgroup/net_cls type cgroup (ro,nosuid,nodev,noexec,relatime,net_cls)
perf_event on /sys/fs/cgroup/perf_event type cgroup (ro,nosuid,nodev,noexec,relatime,perf_event)
net_prio on /sys/fs/cgroup/net_prio type cgroup (ro,nosuid,nodev,noexec,relatime,net_prio)
hugetlb on /sys/fs/cgroup/hugetlb type cgroup (ro,nosuid,nodev,noexec,relatime,hugetlb)
pids on /sys/fs/cgroup/pids type cgroup (ro,nosuid,nodev,noexec,relatime,pids)
cgroup on /sys/fs/cgroup/systemd type cgroup (ro,nosuid,nodev,noexec,relatime,name=systemd)
mqueue on /dev/mqueue type mqueue (rw,nosuid,nodev,noexec,relatime)
//10.0.75.1/C on /data type cifs (rw,relatime,vers=3.02,sec=ntlmsspi,cache=strict,username=filo,domain=MSI,uid=0,noforceuid,gid=0,noforcegid,addr=10.0.75.1,file_mode=0755,dir_mode=0755,iocharset=utf8,nounix,serverino,mapposix,nobrl,mfsymlinks,noperm,rsize=1048576,wsize=1048576,echo_interval=60,actimeo=1)
/dev/sda1 on /etc/resolv.conf type ext4 (rw,relatime,data=ordered)
/dev/sda1 on /etc/hostname type ext4 (rw,relatime,data=ordered)
/dev/sda1 on /etc/hosts type ext4 (rw,relatime,data=ordered)
shm on /dev/shm type tmpfs (rw,nosuid,nodev,noexec,relatime,size=65536k)
devpts on /dev/console type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=666)
proc on /proc/bus type proc (ro,relatime)
proc on /proc/fs type proc (ro,relatime)
proc on /proc/irq type proc (ro,relatime)
proc on /proc/sys type proc (ro,relatime)
proc on /proc/sysrq-trigger type proc (ro,relatime)
tmpfs on /proc/kcore type tmpfs (rw,nosuid,size=65536k,mode=755)
tmpfs on /proc/timer_list type tmpfs (rw,nosuid,size=65536k,mode=755)
tmpfs on /proc/sched_debug type tmpfs (rw,nosuid,size=65536k,mode=755)
tmpfs on /proc/scsi type tmpfs (ro,relatime)
tmpfs on /sys/firmware type tmpfs (ro,relatime)
""",
        0,
        [
            ("/sys/fs/cgroup/perf_event", "cgroup"),
            ("/sys/fs/cgroup/net_prio", "cgroup"),
            ("/sys/fs/cgroup/cpuacct", "cgroup"),
            ("/sys/fs/cgroup/devices", "cgroup"),
            ("/sys/fs/cgroup/freezer", "cgroup"),
            ("/sys/fs/cgroup/net_cls", "cgroup"),
            ("/sys/fs/cgroup/hugetlb", "cgroup"),
            ("/sys/fs/cgroup/systemd", "cgroup"),
            ("/sys/fs/cgroup/cpuset", "cgroup"),
            ("/sys/fs/cgroup/memory", "cgroup"),
            ("/sys/fs/cgroup/blkio", "cgroup"),
            ("/sys/fs/cgroup/pids", "cgroup"),
            ("/proc/sysrq-trigger", "proc"),
            ("/sys/fs/cgroup/cpu", "cgroup"),
            ("/proc/sched_debug", "tmpfs"),
            ("/etc/resolv.conf", "ext4"),
            ("/proc/timer_list", "tmpfs"),
            ("/sys/fs/cgroup", "tmpfs"),
            ("/etc/hostname", "ext4"),
            ("/sys/firmware", "tmpfs"),
            ("/dev/console", "devpts"),
            ("/dev/mqueue", "mqueue"),
            ("/proc/kcore", "tmpfs"),
            ("/etc/hosts", "ext4"),
            ("/proc/scsi", "tmpfs"),
            ("/proc/bus", "proc"),
            ("/proc/irq", "proc"),
            ("/proc/sys", "proc"),
            ("/dev/pts", "devpts"),
            ("/dev/shm", "tmpfs"),
            ("/proc/fs", "proc"),
            ("/proc", "proc"),
            ("/data", "cifs"),
            ("/dev", "tmpfs"),
            ("/sys", "sysfs"),
            ("/", "overlay"),
        ],
    ),
    # From @yarikoptic - added blank lines to test for resilience
    (
        r"""/proc on /proc type proc (rw,relatime)
sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime)
tmpfs on /dev/shm type tmpfs (rw,relatime)
devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=666)

devpts on /dev/ptmx type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=666)

""",
        0,
        [
            ("/dev/ptmx", "devpts"),
            ("/dev/shm", "tmpfs"),
            ("/dev/pts", "devpts"),
            ("/proc", "proc"),
            ("/sys", "sysfs"),
        ],
    ),
)


@pytest.mark.parametrize("output, exit_code, expected", MOUNT_OUTPUTS)
def test_parse_mount_table(output, exit_code, expected):
    assert FsMountIdentifier.parse_mount_table(exit_code, output) == expected


@pytest.mark.skipIf(
    platform.system() == "Windows", reason="Windows does not have mount table"
)
def test_mount_check():
    fake_table = [("/", "ext4"), ("/scratch/tmp", "ext4"), ("/scratch", "cifs")]
    cifs_targets = [
        ("/scratch/tmp/x/y", True),
        ("/scratch/tmp/x", True),
        ("/scratch/x/y", False),
        ("/scratch/x", False),
        ("/x/y", True),
        ("/x", True),
        ("/", True),
    ]

    with FsMountIdentifier.patch_table(fake_table):
        for target, expected in cifs_targets:
            assert FsMountIdentifier.symlinks_supported(target) is expected


def test_copy_constraints(tmp_path):

    ext4_mnt1 = tmp_path / "ext4_mnt1"
    ext4_mnt2 = tmp_path / "ext4_mnt2"
    cifs_mnt = tmp_path / "cifs_mnt"

    fake_mount_table = [
        (str(ext4_mnt1), "ext4"),
        (str(ext4_mnt2), "ext4"),
        (str(cifs_mnt), "cifs"),
    ]

    # Create sample files
    ext4_file = File.sample(dest_dir=ext4_mnt1, seed=1)
    cifs_file = File.sample(dest_dir=cifs_mnt, seed=3)

    with FsMountIdentifier.patch_table(fake_mount_table):
        # Check that symlinks work on ext4
        copy_modes = File.CopyMode.copy | File.CopyMode.hardlink | File.CopyMode.symlink
        new_ext4_file = ext4_file.copy(
            ext4_mnt1 / "dest",
            mode=copy_modes,
        )

        assert new_ext4_file.contents == ext4_file.contents
        assert os.path.islink(new_ext4_file)

        # Symlinks not supported on CIFS
        new_cifs_file = cifs_file.copy(
            cifs_mnt / "dest",
            mode=copy_modes,
        )
        assert new_cifs_file.contents == cifs_file.contents
        assert not os.path.islink(new_cifs_file)
        assert os.stat(new_cifs_file).st_ino == os.stat(cifs_file).st_ino  # Hardlink

        # Hardlinks not supported across logical volumes
        new_ext4_file2 = ext4_file.copy(
            ext4_mnt2 / "dest", mode=File.CopyMode.copy | File.CopyMode.hardlink
        )
        assert new_ext4_file2.contents == ext4_file.contents
        assert not os.path.islink(new_ext4_file2)
        assert (
            os.stat(ext4_file).st_ino != os.stat(new_ext4_file2).st_ino
        )  # Not hardlink

        # Hardlinks not supported across logical volumes 2 (from CIFS)
        ext4_file_on_cifs = ext4_file.copy(
            cifs_mnt / "dest",
            mode=copy_modes,
        )
        assert ext4_file_on_cifs.contents == ext4_file.contents
        assert not os.path.islink(ext4_file_on_cifs)
        assert (
            os.stat(ext4_file).st_ino != os.stat(ext4_file_on_cifs).st_ino
        )  # Not hardlink


def test_generate_mount_table():
    mount_table = FsMountIdentifier.get_mount_table()
    assert isinstance(mount_table, list)
    # We can't test the actual mount table, but we can test that the function actually
    # runs and returns at least one mount/drive
    assert mount_table


@pytest.mark.skipIf(
    platform.system() == "Windows", reason="Windows does not have mount table"
)
def test_symlink_supported():
    assert isinstance(FsMountIdentifier.symlinks_supported("/"), bool)
