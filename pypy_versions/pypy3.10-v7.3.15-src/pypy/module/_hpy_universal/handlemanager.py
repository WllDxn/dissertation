from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.rtyper.annlowlevel import llhelper
from rpython.rlib.objectmodel import specialize, always_inline
from rpython.rlib.unroll import unrolling_iterable
from rpython.rlib.debug import ll_assert
from pypy.interpreter.error import OperationError
from pypy.module._hpy_universal import llapi
from pypy.module._hpy_universal.apiset import API, DEBUG, TRACE
from pypy.objspace.std.capsuleobject import W_Capsule
from .buffer import setup_hpybuffer


@specialize.memo()
def make_missing_function(space, name):
    def missing_function():
        print ("oops! calling the slot '%s', "
               "which is not implemented" % (name,))
        raise OperationError(space.w_NotImplementedError, space.newtext(name))
    return missing_function

CONSTANTS = [
    ('NULL', lambda space: None),
    # Constants
    ('None', lambda space: space.w_None),
    ('True', lambda space: space.w_True),
    ('False', lambda space: space.w_False),
    ('NotImplemented', lambda space: space.w_NotImplemented),
    ('Ellipsis', lambda space: space.w_Ellipsis),
    # Exceptions
    ('BaseException', lambda space: space.w_BaseException),
    ('Exception', lambda space: space.w_Exception),
    ('StopAsyncIteration', lambda space: space.w_StopAsyncIteration),
    ('StopIteration', lambda space: space.w_StopIteration),
    ('GeneratorExit', lambda space: space.w_GeneratorExit),
    ('ArithmeticError', lambda space: space.w_ArithmeticError),
    ('LookupError', lambda space: space.w_LookupError),
    ('AssertionError', lambda space: space.w_AssertionError),
    ('AttributeError', lambda space: space.w_AttributeError),
    ('BufferError', lambda space: space.w_BufferError),
    ('EOFError', lambda space: space.w_EOFError),
    ('FloatingPointError', lambda space: space.w_FloatingPointError),
    ('OSError', lambda space: space.w_OSError),
    ('ImportError', lambda space: space.w_ImportError),
    ('ModuleNotFoundError', lambda space: space.w_ModuleNotFoundError),
    ('IndexError', lambda space: space.w_IndexError),
    ('KeyError', lambda space: space.w_KeyError),
    ('KeyboardInterrupt', lambda space: space.w_KeyboardInterrupt),
    ('MemoryError', lambda space: space.w_MemoryError),
    ('NameError', lambda space: space.w_NameError),
    ('OverflowError', lambda space: space.w_OverflowError),
    ('RuntimeError', lambda space: space.w_RuntimeError),
    ('RecursionError', lambda space: space.w_RecursionError),
    ('NotImplementedError', lambda space: space.w_NotImplementedError),
    ('SyntaxError', lambda space: space.w_SyntaxError),
    ('IndentationError', lambda space: space.w_IndentationError),
    ('TabError', lambda space: space.w_TabError),
    ('ReferenceError', lambda space: space.w_ReferenceError),
    ('SystemError', lambda space: space.w_SystemError),
    ('SystemExit', lambda space: space.w_SystemExit),
    ('TypeError', lambda space: space.w_TypeError),
    ('UnboundLocalError', lambda space: space.w_UnboundLocalError),
    ('UnicodeError', lambda space: space.w_UnicodeError),
    ('UnicodeEncodeError', lambda space: space.w_UnicodeEncodeError),
    ('UnicodeDecodeError', lambda space: space.w_UnicodeDecodeError),
    ('UnicodeTranslateError', lambda space: space.w_UnicodeTranslateError),
    ('ValueError', lambda space: space.w_ValueError),
    ('ZeroDivisionError', lambda space: space.w_ZeroDivisionError),
    ('BlockingIOError', lambda space: space.w_BlockingIOError),
    ('BrokenPipeError', lambda space: space.w_BrokenPipeError),
    ('ChildProcessError', lambda space: space.w_ChildProcessError),
    ('ConnectionError', lambda space: space.w_ConnectionError),
    ('ConnectionAbortedError', lambda space: space.w_ConnectionAbortedError),
    ('ConnectionRefusedError', lambda space: space.w_ConnectionRefusedError),
    ('ConnectionResetError', lambda space: space.w_ConnectionResetError),
    ('FileExistsError', lambda space: space.w_FileExistsError),
    ('FileNotFoundError', lambda space: space.w_FileNotFoundError),
    ('InterruptedError', lambda space: space.w_InterruptedError),
    ('IsADirectoryError', lambda space: space.w_IsADirectoryError),
    ('NotADirectoryError', lambda space: space.w_NotADirectoryError),
    ('PermissionError', lambda space: space.w_PermissionError),
    ('ProcessLookupError', lambda space: space.w_ProcessLookupError),
    ('TimeoutError', lambda space: space.w_TimeoutError),
    # Warnings
    ('Warning', lambda space: space.w_Warning),
    ('UserWarning', lambda space: space.w_UserWarning),
    ('DeprecationWarning', lambda space: space.w_DeprecationWarning),
    ('PendingDeprecationWarning', lambda space: space.w_PendingDeprecationWarning),
    ('SyntaxWarning', lambda space: space.w_SyntaxWarning),
    ('RuntimeWarning', lambda space: space.w_RuntimeWarning),
    ('FutureWarning', lambda space: space.w_FutureWarning),
    ('ImportWarning', lambda space: space.w_ImportWarning),
    ('UnicodeWarning', lambda space: space.w_UnicodeWarning),
    ('BytesWarning', lambda space: space.w_BytesWarning),
    ('ResourceWarning', lambda space: space.w_ResourceWarning),
    # Types
    ('BaseObjectType', lambda space: space.w_object),
    ('TypeType', lambda space: space.w_type),
    ('BoolType', lambda space: space.w_bool),
    ('LongType', lambda space: space.w_int),
    ('FloatType', lambda space: space.w_float),
    ('UnicodeType', lambda space: space.w_unicode),
    ('TupleType', lambda space: space.w_tuple),
    ('ListType', lambda space: space.w_list),
    ('ComplexType', lambda space: space.w_complex),
    ('BytesType', lambda space: space.w_bytes),
    ('MemoryViewType', lambda space: space.w_memoryview),
    ('SliceType', lambda space: space.w_slice),
    ('Builtins', lambda space: space.getattr(space.builtin, space.newtext("__dict__"))),
    ('CapsuleType', lambda space: space.gettypeobject(W_Capsule.typedef)),
]

CONTEXT_FIELDS = unrolling_iterable(llapi.HPyContext.TO._names)
CONSTANT_NAMES = unrolling_iterable([name for name, _ in CONSTANTS])
DUMMY_FUNC = lltype.FuncType([], lltype.Void)

class AbstractHandleManager(object):
    NULL = 0

    def __init__(self, space, is_debug):
        self.space = space
        self.is_debug = is_debug
        # setup a helper class for creating views in the bf_getbuffer slot
        setup_hpybuffer(self)

    def new(self, w_object):
        raise NotImplementedError

    def close(self, index):
        raise NotImplementedError

    def deref(self, index):
        raise NotImplementedError

    def consume(self, index):
        raise NotImplementedError

    def dup(self, index):
        raise NotImplementedError

    def attach_release_callback(self, index, cb):
        raise NotImplementedError

    def get_ctx(self):
        raise NotImplementedError

    @specialize.arg(0)
    def using(self, *w_objs):
        """
        context-manager to new/close one or more handles
        """
        # Here we are using some RPython trickery to create different classes
        # depending on the number of w_objs. The idea is that the whole class is
        # optimized away and what's left is a series of calls to handles.new() and
        # handles.close()
        UsingContextManager = make_UsingContextManager(self, len(w_objs))
        return UsingContextManager(w_objs)

    def _freeze_(self):
        return True


class HandleManager(AbstractHandleManager):
    cls_suffix = '_u'

    def __init__(self, space, uctx):
        from .interp_extfunc import W_ExtensionFunction_u, W_ExtensionMethod_u
        AbstractHandleManager.__init__(self, space, is_debug=False)
        self.ctx = uctx
        self.handles_w = [build_value(space) for name, build_value in CONSTANTS]
        self.release_callbacks = [None] * len(self.handles_w)
        self.free_list = []
        self.w_ExtensionFunction = W_ExtensionFunction_u
        self.w_ExtensionMethod = W_ExtensionMethod_u

    @staticmethod
    @specialize.memo()
    def ctx_name():
        # by using specialize.memo() this becomes a statically allocated
        # charp, like a C string literal
        return rffi.str2constcharp("HPy Universal ABI (PyPy backend)",
                                   track_allocation=False)

    def setup_universal_ctx(self):
        space = self.space
        self.ctx.c_name = self.ctx_name()

        for name in CONTEXT_FIELDS:
            if name == 'c_abi_version':
                continue
            if name.startswith('c_ctx_'):
                # this is a function pointer: assign a default value so we get
                # a reasonable error message if it's called without being
                # assigned to something else
                missing_function = make_missing_function(space, name)
                funcptr = llhelper(lltype.Ptr(DUMMY_FUNC), missing_function)
                setattr(self.ctx, name, rffi.cast(rffi.VOIDP, funcptr))
        i = 0
        for name in CONSTANT_NAMES:
            if name != 'NULL':
                h_struct = getattr(self.ctx, 'c_h_' + name)
                h_struct.c__i = i
            i = i + 1

        for func in API.all_functions:
            if func.cpyext and not space.config.objspace.hpy_cpyext_API:
                # ignore cpyext functions if hpy_cpyext_API is False
                continue
            if func.is_helper:
                # helper functions don't go into the context
                continue
            funcptr = rffi.cast(rffi.VOIDP, func.get_llhelper(space))
            ctx_field = 'c_ctx_' + func.basename
            setattr(self.ctx, ctx_field, funcptr)

        self.ctx.c_ctx_FatalError = rffi.cast(rffi.VOIDP, llapi.pypy_HPy_FatalError)

    def get_ctx(self):
        return self.ctx

    def new(self, w_object):
        if len(self.free_list) == 0:
            index = len(self.handles_w)
            self.handles_w.append(w_object)
            self.release_callbacks.append(None)
        else:
            index = self.free_list.pop()
            self.handles_w[index] = w_object
        return index

    def close(self, index):
        ll_assert(index > 0, 'HandleManager.close: index > 0')
        if self.release_callbacks[index] is not None:
            self._call_release_callbacks(index)
        self.handles_w[index] = None
        self.free_list.append(index)

    def _call_release_callbacks(self, index):
        w_obj = self.deref(index)
        for f in self.release_callbacks[index]:
            f.release(index, w_obj)
        self.release_callbacks[index] = None

    def deref(self, index):
        assert index > 0
        return self.handles_w[index]

    def consume(self, index):
        """
        Like close, but also return the w_object which was pointed by the handled
        """
        assert index > 0
        w_object = self.handles_w[index]
        self.close(index)
        return w_object

    def dup(self, index):
        assert index > 0
        w_object = self.handles_w[index]
        return self.new(w_object)

    def attach_release_callback(self, index, cb):
        assert index > 0
        if self.release_callbacks[index] is None:
            self.release_callbacks[index] = [cb]
        else:
            self.release_callbacks[index].append(cb)

    def str2ownedptr(self, s, owner):
        # Used in converting a string to a `const char *` via a non-moving buffer
        llbuf, llstring, flag = rffi.get_nonmovingbuffer_ll_final_null(s)
        cb = FreeNonMovingBuffer(llbuf, llstring, flag)
        self.attach_release_callback(owner, cb)
        return llbuf


class DebugHandleManager(AbstractHandleManager):
    cls_suffix = '_d'

    def __init__(self, space, dctx, u_handles):
        from .interp_extfunc import W_ExtensionFunction_d, W_ExtensionMethod_d
        AbstractHandleManager.__init__(self, space, is_debug=True)
        self.ctx = dctx
        self.u_handles = u_handles
        self.w_ExtensionFunction = W_ExtensionFunction_d
        self.w_ExtensionMethod = W_ExtensionMethod_d

    @staticmethod
    @specialize.memo()
    def ctx_name():
        # by using specialize.memo() this becomes a statically allocated
        # charp, like a C string literal
        return rffi.str2constcharp("HPy Debug Mode ABI (PyPy backend)",
                                   track_allocation=False)

    def setup_debug_ctx(self):
        space = self.space
        self.ctx.c_name = self.ctx_name()
        rffi.setintfield(self.ctx, 'c_abi_version', 0)
        self.ctx.c__private = llapi.cts.cast('void*', 0)
        llapi.hpy_debug_ctx_init(self.ctx, self.u_handles.ctx)
        for func in DEBUG.all_functions:
            funcptr = rffi.cast(rffi.VOIDP, func.get_llhelper(space))
            ctx_field = 'c_ctx_' + func.basename
            setattr(self.ctx, ctx_field, funcptr)
        llapi.hpy_debug_set_ctx(self.ctx)

    def get_ctx(self):
        return self.ctx

    def new(self, w_object):
        uh = self.u_handles.new(w_object)
        ret = llapi.hpy_debug_open_handle(self.ctx, uh)
        # print 'debug new', ret, uh
        return ret

    def close(self, dh):
        # tricky, we need to deref dh but use index for all self.u_handles interactions
        index = llapi.hpy_debug_unwrap_handle(self.ctx, dh)
        ll_assert(index > 0, 'HandleManager.close: index > 0')
        # print 'debug close', index, dh
        llapi.hpy_debug_close_handle(self.ctx, dh)
        self.u_handles.close(index)

    def deref(self, dh):
        # print 'deref', dh
        uh = llapi.hpy_debug_unwrap_handle(self.ctx, dh)
        return self.u_handles.deref(uh)

    def consume(self, dh):
        uh = llapi.hpy_debug_unwrap_handle(self.ctx, dh)
        llapi.hpy_debug_close_handle(self.ctx, dh)
        return self.u_handles.consume(uh)

    def dup(self, dh):
        uh = llapi.hpy_debug_unwrap_handle(self.ctx, dh)
        new_uh = self.u_handles.dup(uh)
        w_object = self.u_handles.deref(new_uh)
        ret = self.new(w_object)
        # print 'dup', dh, uh, w_object, 'returning', ret
        return ret

    def attach_release_callback(self, index, cb):
        uh = llapi.hpy_debug_unwrap_handle(self.ctx, index)
        self.u_handles.attach_release_callback(uh, cb)

    def str2ownedptr(self, s, owner):
        return self.u_handles.str2ownedptr(s, owner)

class TraceHandleManager(AbstractHandleManager):
    cls_suffix = '_t'

    def __init__(self, space, u_handles):
        from .interp_extfunc import W_ExtensionFunction_t, W_ExtensionMethod_t
        AbstractHandleManager.__init__(self, space, is_debug=False)
        self.u_handles = u_handles
        self.w_ExtensionFunction = W_ExtensionFunction_t
        self.w_ExtensionMethod = W_ExtensionMethod_t

    @staticmethod
    @specialize.memo()
    def ctx_name():
        # by using specialize.memo() this becomes a statically allocated
        # charp, like a C string literal
        return rffi.str2constcharp("HPy Trace Mode ABI (PyPy backend)",
                                   track_allocation=False)

    def setup_trace_ctx(self):
        space = self.space
        ctx = llapi.hpy_trace_get_ctx(self.u_handles.ctx)
        ctx.c_name = self.ctx_name()
        rffi.setintfield(ctx, 'c_abi_version', 0)
        ctx.c__private = llapi.cts.cast('void*', 0)
        llapi.hpy_trace_ctx_init(ctx, self.u_handles.ctx)
        for func in TRACE.all_functions:
            funcptr = rffi.cast(rffi.VOIDP, func.get_llhelper(space))
            ctx_field = 'c_ctx_' + func.basename
            setattr(ctx, ctx_field, funcptr)

    def get_ctx(self):
        return llapi.hpy_trace_get_ctx(self.u_handles.ctx)

    def new(self, w_object):
        return self.u_handles.new(w_object)

    def close(self, index):
        return self.u_handles.close(index)

    def consume(self, index):
        return self.u_handles.consume(index)


class HandleReleaseCallback(object):

    def release(self, h, w_obj):
        ll_assert(False, 'HandleReleaseCallback.release: not implemented')


class FreeNonMovingBuffer(HandleReleaseCallback):
    """
    Callback to call rffi.free_nonmovingbuffer_ll
    """

    def __init__(self, llbuf, llstring, flag):
        self.llbuf = llbuf
        self.llstring = llstring
        self.flag = flag

    def release(self, h, w_obj):
        rffi.free_nonmovingbuffer_ll(self.llbuf, self.llstring, self.flag)


@specialize.memo()
def make_UsingContextManager(mgr, N):
    INDICES = unrolling_iterable(range(N))
    class UsingContextManager(object):

        @always_inline
        def __init__(self, w_objects):
            self.w_objects = w_objects
            self.handles = (0,) * N

        #@always_inline
        def __enter__(self):
            handles = ()
            for i in INDICES:
                h = mgr.new(self.w_objects[i])
                handles += (h,)
            self.handles = handles

            # if we have only one handle, return it directly. This makes it
            # possible to write this:
            #     with handles.using(w1) as h1:
            #         ...
            # AND this
            #     with handles.using(w1, w2) as (h1, h2):
            #         ...
            if N == 1:
                return self.handles[0]
            else:
                return handles

        #@always_inline
        def __exit__(self, etype, evalue, tb):
            for i in INDICES:
                mgr.close(self.handles[i])

    return UsingContextManager
