"""Restrict this Linux build process and its children from network access.

This adds a seccomp restriction; it never changes existing sandbox permissions.
Call before importing the speech runtime so even native telemetry cannot connect.
"""
import ctypes
import ctypes.util
import errno
import socket


def disable_network():
    lib = ctypes.CDLL(ctypes.util.find_library('seccomp') or 'libseccomp.so.2')
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
    lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    context = lib.seccomp_init(0x7FFF0000)  # Allow non-network system calls.
    if not context:
        raise RuntimeError('Could not initialize offline guard')
    try:
        for name in [b'socket', b'connect', b'sendto', b'sendmsg', b'sendmmsg']:
            syscall = lib.seccomp_syscall_resolve_name(name)
            if syscall < 0 or lib.seccomp_rule_add(context, 0x00050000 | errno.EPERM, syscall, 0):
                raise RuntimeError('Could not restrict network system calls')
        if lib.seccomp_load(context):
            raise RuntimeError('Could not activate offline guard')
    finally:
        lib.seccomp_release(context)
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except PermissionError:
        print('Offline guard verified: network sockets are denied.', flush=True)
    else:
        connection.close()
        raise RuntimeError('Offline guard verification failed')


if __name__ == '__main__':
    disable_network()
