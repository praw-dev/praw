"""A function to validate the types of a paramter."""


def validate_types(
    variable,
    expected_types,
    ignore_none=True,
    _internal_call=False,
    variable_name=None,
    expected_type_names=None,
    error_message=None,
    error_class=TypeError,
):
    """A function to make sure the values that are entered in a function are the correct types that should be entered
    in order to not cause any weird behavior with mismatched types.

    If the given variable does not match the expected types, then an error, default TypeError, is thrown.

    .. note:: By default, it does not throw an error if the variable is the value `None`, however this can be changed
       by setting the parameter ignore_none to False.

    :param variable: The variable that should be type-checked

    :param expected_types: A type or tuple of types that should be matched to the variable. These are the type(s) that
        the variable should be.

    :param variable_name: The name of the variable that shows up in the error. This does not need to be included if the
        parameter error_message is not None. If error_message is None, then not including this argument will raise a
        ValueError

    :param ignore_none: A boolean stating whether or not to not throw an error if the variable is None. Default true.

    :param _internal_call: A boolean stating if the function is calling itself internally. Default false.

        .. warning:: This variable should never be set to true if not being called from inside the function.

    :param expected_type_names: A list of strings that correspond to the type(s) that are expected. If not given,
        they will be automatically calculated from the name of the given type(s). This does not need to be included
        if the parameter error_message is not None.

    :param error_message: A message to override the default message that is dynamically calculated.

    :param error_class: The error class to raise, default TypeError.

    If a variable does match, nothing is returned.

    .. code:: python

        url = "12"
        validate_types(url, str, variable_name = "url")
        # passes, returns None

    However, if a variable does not match, a TypeError is raised.

    .. code:: python

        id = 12
        validate_types(id, str, variable_name = "id")
        # raises TypeError("The variable 'id' must be type `str` (was type `int`).")

    Multiple types must be specified in a collection such as a list, tuple or set.

    .. code:: python

        id_list = {"id1": "1", "id2": "2"}
        validate_types(id_list, (list, tuple, set), variable_name = "id")
        # raises TypeError("The variable 'id_list' must be types `list`, `tuple` or `set` (was type `dict`).)

    The names for expected types can be provided in a mix of strings and types.

    .. code:: python

        types_list = (str, int, "Imaginary numbers", type)
        validate_types(30.6, (str, int, type), variable_name="id", expected_type_names = types_list)
        # raises TypeError("The variable 'id' must be types `str`, `int`, `Imaginary numbers` or `type`
                            (was type `float`).")

    The error message that is printed can be changed completely.

    It can be a static message, where the exception will raise exactly what was provided.

    .. code:: python

        msg = "You provided the wrong type"
        example = 4
        validate_types(example, str, error_message = msg)
        # raises TypeError("You provided the wrong type")

    You can also provide a string with three string-format values ('%s') and the function will auto-substitute
    in values in the order:

        1. Variable name
        2. Type strings in format `<typename>`, ..., or `<typename>`
        3. The actual type in format `<typename>`

    .. code:: python

        msg = "WRONG TYPES, NAME: %s, EXPECTED: %s, GOT: %s"
        example = "$"
        validate_types(example, (int, float), variable_name="example", error_message=msg)
        # raises TypeError("WRONG TYPES, NAME: example, EXPECTED: `int` or `float`, GOT: `str`")

    """

    fail = False
    if not _internal_call:
        validate_types(
            variable_name,
            str,
            variable_name="variable_name",
            _internal_call=True,
        )
        validate_types(
            expected_types,
            (type, list, tuple, set),
            variable_name="expected_types",
            _internal_call=True,
        )
        validate_types(
            ignore_none,
            (int, bool),
            variable_name="ignore_none",
            _internal_call=True,
        )
        validate_types(
            error_message,
            str,
            variable_name="error_message",
            _internal_call=True,
        )
        validate_types(
            error_class, type, variable_name="error_class", _internal_call=True
        )
        validate_types(
            expected_type_names,
            (str, list, tuple, set, type),
            variable_name="expected_type_names",
            _internal_call = True,
        )
        if error_message is None and variable_name is None:
            raise ValueError(
                "variable_name needs to be specified if error_message is not given"
            )
        elif error_message is not None and variable_name is not None:
            if error_message.count("%s") != 3:
                raise ValueError(
                    "Both error_message and variable_name has been specified. Please only specify one."
                )
        elif error_message is not None and variable_name is None:
            if error_message.count("%s") == 3:
                raise ValueError(
                    "variable_name needs to be specified if error_message contains the correct amount of string "
                    "substitution modifiers."
                )
        if expected_types is None:
            if variable is None:
                return None
        if hasattr(expected_types, "__iter__") and not isinstance(expected_types, type):
            if None in expected_types:
                if variable is None:
                    return None
    if not ignore_none and variable is None:
        fail = True
    if ignore_none:
        if not isinstance(variable, expected_types) and variable is not None:
            fail = True
    if fail:
        vlist = []
        if not isinstance(expected_types, type):
            msg = "The variable '%s' must be types %s (was type %s)."
        else:
            try:
                if len(expected_types) > 1:
                    msg = "The variable '%s' must be types %s (was type %s)."
                else:
                    msg = "The variable '%s' must be type %s (was type %s)."
            except TypeError:
                msg = "The variable '%s' must be type %s (was type %s)."
        if isinstance(expected_type_names, (str, type)):
            expected_type_names = (expected_type_names,)
        if expected_type_names is not None:
            for vtype in expected_type_names:
                if not _internal_call:
                    validate_types(
                        vtype,
                        (str, type),
                        variable_name=expected_type_names,
                        _internal_call=True,
                        expected_type_names=[
                            "Iterable[str]",
                            "[Iterable[type]",
                        ],
                    )
                if isinstance(vtype, type):
                    vlist.append(vtype.__name__)
                else:
                    vlist.append(vtype)
        else:
            if isinstance(expected_types, (type, None.__class__)):
                expected_types = (expected_types,)
            for type_ in expected_types:
                try:
                    vlist.append(type_.__name__)
                except AttributeError:
                    vlist.append(str(type_))
        if len(vlist) > 1:
            prelim_vals = vlist[:-1]
            varmsg = ""
            for val in prelim_vals:
                varmsg += "`%s`, " % val
            varmsg = varmsg.rstrip(", ") + " "
            varmsg += "or `%s`" % vlist[-1]
        else:
            varmsg = "`%s`" % vlist[-1]
        if error_message is not None:
            if error_message.count("%s") == 3:
                msg = error_message
            else:
                raise error_class(error_message)
        raise error_class(
            msg % (variable_name, varmsg, "`%s`" % variable.__class__.__name__)
        )
