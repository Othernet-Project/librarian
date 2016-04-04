###!
@author Outenet Inc <apps@outernet.is>
@license GPLv3, LGPL, MIT
###

# # DaHelpers
#
# These are da helpers to help you out.
#
# A growing collection of miscellaneous general-purpose helper function for
# JavaScript in browsers and on NodeJS.
#
# ::TOC::
#
# This module is in UMD format and will create a `dahelpers` global in browsers
# when not used with an AMD loader such as RequireJS.
#
define = ((root) ->
  if typeof root.define is 'function' and root.define.amd
    root.define
  else
    if typeof module is 'object' and module.exports
      (factory) -> module.exports = factory()
    else
      (factory) -> root.dahelpers = factory()
)(this)

define () ->

  # This module has no external dependencies.
  #

  h =

    # ## Variables
    #
    # The module contains variables that you can modify to influence the
    # behavior of some of the functions.
    #

    # ### `#USD`
    #
    # Symbol for US currency. Default is '$'.
    #
    USD: '$'

    # ### `#EUR`
    #
    # Symbol for EU currency. Default is '€'.
    #
    EUR: '€'

    # ### `#YN`
    #
    # Symbol for Japanese and Chinese currencies. Default is '¥'.
    #
    YN: '¥'

    # ### `#GBP`
    #
    # Symbol for UK currency. Default is '£'.
    #
    GBP: '£'

    # ### `#DEFAULT_CURRENCY`
    #
    # Default curency used by `#currency()` function. Default is '$'.
    #
    DEFAULT_CURRENCY: '$'

    # ### `#FIRST_CHAR`
    #
    # Regular expression for capturing the first character of a word. Default
    # is `/\b[a-z]/gi`. Please see documentation for the
    # [`#titleCase()`](#titlecase-s-lowerfirst] for information on how this
    # variable is used.
    #
    FIRST_CHAR: /\b[a-z]/gi

    # ### `#WRAP_WIDTH`
    #
    # Default text wrap width.
    #
    WRAP_WIDTH: 79

    # ### `#FORMAT_CHARACTER`
    #
    # Character used by default in [`#format()`](#format-s-format-formatchar)
    # function.
    #
    FORMAT_CHARACTER: '#'

    # ### `#PLURAL_RULES`
    #
    # Returns the form to use based on number `n`. The form is 0 for singular,
    # and 1 or more for plural forms.
    #
    # This function is called by the
    # [`#plural()`](#plural-singular-plural-plural2-count) function to yield
    # the correct form.
    #
    # Default function accounts for English and compatible pluralization where
    # singular is used when n==1, and a single plural form for all other cases.
    #
    # You can see different rules for different languages at [Unicode
    # CLDR](http://www.unicode.org/cldr/charts/supplemental/language_plural_rules.html).
    #
    PLURAL_RULES: (n) ->
      if n is 1 then 0 else 1

    # ### `#HTML_ESCAPE_MAPPINGS`
    #
    # Mapping used to escape HTML.
    #
    HTML_ESCAPE_MAPPINGS:
      '&': '&amp;'
      '<': '&lt;'
      '>': '&gt;'
      '"': '&quot;'
      "'": '&#x27;'
      '/': '&#x2F;'

    # ## Logic, type detection
    #

    # ### `#type(v, type)`
    #
    # Tests if `v` is of type `type`. The valid types are:
    #
    #  + 'null'
    #  + 'undefined'
    #  + 'string'
    #  + 'number'
    #  + 'date'
    #  + 'regexp'
    #  + 'array'
    #  + 'function'
    #  + 'object'
    #
    # Note that this function can be reliably used as a replacement for
    # `typeOf` function and differentiates between more object types.
    #
    # If the `type` argument is not supplied, it will return the type of the
    # value.
    #
    # Example:
    #
    #     dahelpers.type([], 'array');
    #     // returns true
    #     dahelpers.type([])
    #     // returns 'array'
    #
    type: (v, type) ->
      t = Object::toString.call(v).toLowerCase()[8..-2]
      return t if not type?
      t is type.toLowerCase()

    # ### `#klass(v, klass)`
    #
    # Tests if `v` has constructor of `klass`. If `v` is not an object, it
    # returns `false`.
    #
    # If the `klass` argument is missing, returns the constructor.
    #
    # Example:
    #
    #     dahelpers.klass({});
    #     // returns `Object` (function)
    #     dahelpers.klass([], Array);
    #     // returns `true`
    #
    klass: (v, klass) ->
      return false if typeof v isnt 'object' or v is null
      if klass?
        v.constructor is klass
      else
        v.constructor

    # ### `#truth(v)`
    #
    # A more pragmatic truthy and falsy.
    #
    # This function returns `false` for the following values:
    #
    #  + `undefined`
    #  + `null`
    #  + `0`
    #  + `''`
    #  + `false`
    #  + `{}`
    #  + `[]`
    #
    # For all other values, it will return `true`.
    #
    # Examples:
    #
    #     var truth = dahelpers.truth;
    #     truth(12);     // true
    #     truth(null);   // false
    #     truth('foo');  // true
    #     truth('');     // false
    #
    truth: (v) ->
      return false if h.type(v, 'undefined') or h.type(v, 'null')
      return false if v is 0
      return false if v is ''
      return false if v is false
      if h.type(v, 'object') or h.type(v, 'array')
        not h.empty v
      else
        true

    # ### `#every(arr)`
    #
    # Return true if all elements in `arr` array are truthy.
    #
    # Example:
    #
    #     var a = [1, true, 'foo'];
    #     var b = [1, false, 'foo'];
    #     dahelpers.every(a); // true
    #     dahelpers.every(b); // false
    #
    every: (arr) ->
      for item in arr
        return false if not item
      true

    # ### `#none(arr)`
    #
    # Return true if none of the elements in `arr` array are truthy.
    #
    # Example:
    #
    #     var a = [false, undefined, null, 0];
    #     var b = [false, 'foo', null, 0];
    #     dahelpers.none(a); // true
    #     dahelpers.none(b); // false
    #
    none: (arr) ->
      for item in arr
        return false if item
      true

    # ### `#any(arr)`
    #
    # Return true if at least one item in array is truthy.
    #
    # This function is a reverse of `#none()`.
    #
    # Example:
    #
    #     var a = [false, undefined, null, 0];
    #     var b = [false, 'foo', null, 0];
    #     dahelpers.none(a); // false
    #     dahelpers.none(b); // true
    #
    any: (arr) ->
      not h.none(arr)

    # ### `#toArray(v)`
    #
    # Converts `v` to an array if it's not an array.
    #
    # Example:
    #
    #     a = 'foo'
    #     dahelpers.toArray(a);
    #     // returns ['foo']
    #
    toArray: (v) ->
      return [] if not v?
      if h.type(v, 'array') then v else [v]

    # ### `#empty(v)`
    #
    # Tests if `v` is an empty object, array, or string.
    #
    # Always returns undefined if `v` is not array, object, nor string.
    #
    # Examples:
    #
    #     dahelpers.empty({});         // true
    #     dahelpers.empty([]);         // true
    #     dahelpers.empty(1);          // undefined
    #     dahelpers.empty([1,2,3]);    // false
    #     dahelpers.empty('');         // true
    #     dahelpers.empty('foo bar');  // false
    #
    empty: (v) ->
      if h.type(v, 'array') or h.type(v, 'string')
        not v.length
      else if h.type(v, 'object')
        not (k for k of v).length

    # ## Working with objects
    #

    # ### `#props(o, p)`
    #
    # Get a value of a property tree `p` on the object `o` or undefined if any
    # of the segments is undefined without throwing an exception.
    #
    # Example:
    #
    #     var obj = {foo: {bar: {baz: 1}}};
    #     dahelpers.props(obj, 'foo.bar.baz'); // returns 1
    #     dahelpers.props(obj, 'foo.foo.baz'); // returns undefined
    #
    props: (o, p) ->
      return if not o?
      return o if not p?
      p = p.split('.') if h.type(p) isnt 'array'
      [f, r...] = p
      if not r.length
        return o[f]
      else
        if not o[f]? then undefined else h.props o[f], r.join('.')

    # ### `#propset(o, p, [v])`
    #
    # Sets the value of the property tree `p`'s last leaf to `v` creating all
    # intermediate segments as necessary.
    #
    # The `p` argument can also be an array.
    #
    # Example:
    #
    #     var obj = {}
    #     dahelpers.propset(obj, 'a.b.c.d.e.f', 1);
    #     // obj is now {a: {b: {c: {d: {e: {f: 1}}}}}}
    #
    #     var obj = {}
    #     dahelpers.propset(obj, ['a', 'b', 'c', 'd', 'e', 'f'], 1);
    #     // obj is now {a: {b: {c: {d: {e: {f: 1}}}}}}
    #
    propset: (o, p, v) ->
      return if not o?
      return o if (not p?) or not p.length
      p = p.split('.') if h.type p, 'string'
      [f, r...] = p
      if not r.length
        o[f] = v
      else
        o[f] or= {}
      h.propset o[f], r, v
      o

    # ### `#walk(obj, cb)`
    #
    # Recursively walks down `obj`'s properties and invokes the callback on
    # each one.
    #
    # The callback function takes three arguments. The first argument is the
    # property currently being iterated, and the second argument is the name of
    # the key. The key name will be a full property path. For example a key
    # name for `obj.foo.bar.baz` would be 'foo.bar.baz' (see example). Third
    # argument is an array of key components that make up the second parameter.
    # The key components array is generally more precise since it correctly
    # handles cases where a period may be part of the key.
    #
    # The undocumented `key` and `comps` argument is an internal implementation
    # detail, and should not be be passed under normal circumstances.
    #
    # Example:
    #
    #     var obj = {a: 1, b: 2, c: {a: 1, b: 2}};
    #     dahelpers.walk(obj, console.log);
    #     // Logs:
    #     // 1 a
    #     // 2 b
    #     // Object { a=1, b=2 } c
    #     // 1 c.a
    #     // 2 c.b
    #
    walk: (obj, cb, key=null, comps=[]) ->
      if obj is Object(obj) and obj.constructor is Object
        cb(obj, key, comps) if key isnt null  # Do once for the entire subtree
        for k of obj
          h.walk obj[k], cb, (if key then [key, k].join('.') else k), comps.concat [k]
        return
      else
        cb obj, key, comps
        return

    # ### `#sweep(obj, cb)`
    #
    # Sweeps over the object attributes, and calls the callback on each key.
    # The return value of the callback is used to build a new object with the
    # same property structure as the old one.
    #
    # This function is similar to `#walk()` and uses walk to iterate over the
    # object.
    #
    # The callback function takes four arguments:
    #
    #  + the value of the key
    #  + the full key (e.g, 'foo.bar.baz' for `obj.foo.bar.baz`)
    #  + boolean flag which is `true` if value is an object
    #
    # The reason for the latter is that the value's properties will also be
    # iterated when a value is an object, so you may want to adjust the
    # handling of that case.
    #
    # If the callback function returns undefined, the matching property will
    # not be set at all on the resulting object.
    #
    # Example:
    #
    #     obj = {a: 1, b: 2, c: 3}
    #     dahelpers.sweep(obj, function(v) { return v + 1; });
    #     // Returns {a: 2, b: 3, c: 4}
    #
    sweep: (obj, cb) ->
      ((o) ->
        h.walk obj, (v, k) ->
          isObj = v is Object(v) and h.klass(v, Object)
          v1 = cb(v, k, isObj)
          h.propset o, k, v1 if not h.type(v1, 'undefined')
        o
      ) {}

    # ### `#extend([guard], obj, mixin, [mixin...])`
    #
    # Deep-copies properties from `mixin`s into `obj`. Any properties that are
    # already present in `obj` will be overwritten by properties in mixins.
    #
    # It currently does not clone items within arrays embedded in objects. It
    # just crates a new array containing the same objects as the original one.
    #
    # The optional `guard` function can be passed that prevents setting of a
    # mixin property when it returns `true`. The guard has the following
    # signature:
    #
    #     guard(obj, value, keys, components)
    #
    #  + `obj`: Child object
    #  + `value`: Value of the mixin key currently being processed
    #  + `keys`: The full key path (e.g., 'foo.bar.baz')
    #  + `components`: The full key path as array (e.g., ['foo', 'bar', 'baz'])
    #
    # Default guard returns `false` if the the `value` is `undefined`. Note
    # that this behavior is completely overridden by a guard function if one is
    # specified.
    #
    # Example:
    #
    #     obj = {foo: 1, bar: {baz: new Date(2013, 8, 1)}};
    #     obj1 = {foo: 2, baz: 3};
    #     dahelpers.extend(obj, obj1)
    #     // `obj` should now be:
    #     // {foo: 2, bar: {baz: Date(2013, 8, 1)}, baz: 3}
    #
    extend: (obj, mixins...) ->
      if h.type obj, 'function'
        guard = obj
        [obj, mixins...] = mixins
      else
        guard = (obj, v) -> h.type(v) isnt 'undefined'

      for mixin in mixins
        h.walk mixin, (v, k, c) ->
          return if not guard obj, v, k, c

          if h.klass(v) is false
            h.propset obj, c, v

          else
            h.propset obj, c, (() ->
              switch h.klass(v)
                when Object then {}
                when Date then new Date v.getTime()
                when RegExp then new RegExp v
                when Array then v[0..]
                else v
            )()
      obj

    # ### `#mixin(obj, mixin, [mixin...])`
    #
    # Deep-copies properties from `mixin`s into `obj` only when `obj` does
    # not already have the property.
    #
    # Main difference between the `#extend()` and `#mixin()` is the way
    # existing properties on `obj` are handled. The `#extend()` function simply
    # overwrites existing properties, whereas `#mixin()` doesn't. Otherwise,
    # they are both identical, and, in fact, `#mixin()` is a simple wrapper
    # around `#extend()` that uses a slightly different guard function.
    #
    # Example:
    #
    #     obj = {foo: 1, bar: {baz: new Date(2013, 8, 1)}};
    #     obj1 = {foo: 2, baz: 3};
    #     dahelpers.mixin(obj, obj1)
    #     // `obj` should now be:
    #     // {foo: 1, bar: {baz: Date(2013, 8, 1)}, baz: 3}
    #     // Note that `foo` is still 1 unlike with `#extend()`
    #
    mixin: (obj, mixins...) ->
      guard = (obj, v, k, c) ->
        return false if h.type(v) is 'undefined'
        propType = h.type(h.props(obj, c))
        propType is 'undefined'
      h.extend.apply null, [guard, obj].concat mixins

    # ### `#create(parent, mixin)`
    #
    # Prototypal inhertiance as per Douglas Crockford's recipe with support for
    # mixins.
    #
    # The created object additionally has a `__super__` property which points
    # to the parent object.
    #
    create: (parent, mixins...) ->
      Child = () ->
        h.extend.apply null, [this].concat mixins
        @__super__ = parent
        @
      Child.prototype = parent
      new Child()

    # ### `#clone(obj)`
    #
    # Returns an exact clone of `obj`.
    #
    # It currently does not clone items within arrays embedded in objects. It
    # just crates a new array containing the same objects as the original one.
    #
    # Example:
    #
    #     obj = {foo: 1, bar: {baz: new Date(2013, 8, 1)}};
    #     obj1 = dahelpers.clone(obj)
    #     obj1.bar.baz.setFullYear(2020);
    #     obj.bar.baz.getFullYear() == obj1.bar.baz.getFullYear()
    #     // Should be `false`
    #
    clone: (obj) ->
      return obj if not h.klass(obj, Object)
      h.extend {}, obj

    # ### `#rekey(obj, map)`
    #
    # Creates a new object whose keys are translated to new names using `map`.
    #
    # `map` should be a simple object that maps original keys to new keys. Both
    # original and new keys can be full property subtrees.
    #
    # The target structure is unrelated to source structure, so an object of
    # arbitrary complexity (or simplicity) can be created from any object.
    #
    # Any keys that are not found in the map will not be present in the new
    # object. Keys that are undefined in the original object will also not be
    # present in the new object.
    #
    # Example:
    #
    #     var obj = {
    #       a: {
    #         b: 1,
    #         c: 2
    #       },
    #       d: {
    #         e: 3,
    #         f: 4
    #       }
    #     };
    #
    #     dahelpers.rekey(obj, {
    #       'a.b', 'aa.b.bb',
    #       'a.c', 'aa.b.cc',
    #       'a.d', 'aa.b.dd'
    #     })
    #     // Returns
    #     // {aa: b: {{bb: 1, cc: 1}}}
    #
    rekey: (obj, map) ->
      return if not obj
      return obj if h.klass(obj) is false
      return h.clone(obj) if not h.type(map, 'object')
      newObj = {}
      for source, target of map
        h.propset newObj, target, h.props obj, source
      newObj

    # ### `#subset(small, big)`
    #
    # Returns true if `small` object is a subset of `big` object.
    #
    # Subset means that all key-value pairs of one object is contained within
    # another.
    #
    # Example:
    #
    #     var a = {a: 1, b: 2, c: 3};
    #     var b = {a: 1};
    #     var d = {d: 2};
    #     dahelpers.subset(b, a); // true
    #     dahelpers.subset(d, a); // false
    #     dahelpers.subset(a, b); // false
    #
    subset: (small, big) ->
      try
        h.walk small, (v, k, c) ->
          throw new Error() if not (v is h.props big, c)
      catch
        return false
      return true

    # ## Working with arrays
    #

    # ### `#pair(keys, values)`
    #
    # Returns an object whose keys are taken from the first argument, and
    # mapped to values in the second argument.
    #
    # Eample:
    #
    #     var a1 = ['foo', 'bar'];
    #     var a2 = [1, 2];
    #     dahelpers.pair(a1, a2);
    #     // returns {foo: 1, bar: 2}
    #
    pair: (keys, values) ->
      if keys.length isnt values.length
        throw new TypeError 'Key-value mismatch'
      o = {}
      for key, idx in keys
        o[key] = values[idx]
      o

    # ### `#unpair(o)`
    #
    # Returns a two-member array where the first memeber is an array of keys,
    # and second member is an array of values.
    #
    # Example:
    #
    #     var o = {foo: 1, bar: 2};
    #     dahelpers.unpair(o);
    #     // returns [['foo', 'bar'], [1, 2]]
    #
    unpair: (o) ->
      keys = []
      vals = []
      for key, val of o
        keys.push key
        vals.push val
      [keys, vals]

    # ### `#zip(array, [array...])`
    #
    # Returns an array when each member is an array of members with the
    # corresponding index from all arrays passed to this function. The
    # resulting array is as long as the shortest array.
    #
    # Example:
    #
    #     var a = [1, 2, 3, 4];
    #     var b = [11, 12, 13];
    #     var c = [101, 102, 103];
    #     dahelpers.zip(a, b, c);
    #     // returns [[1, 11, 101], [2, 12, 102], [3, 13, 103]]
    #
    zip: (arrays...) ->
      shortest = Math.min (a.length for a in arrays)...
      res = []
      for i in [0..shortest - 1]
        a = []
        for arr in arrays
          a.push arr[i]
        res.push a
      res

    # ## Iteration
    #

    iterBase: (state) ->
      indices: () ->
        state.indices

      len: () ->
        state.length

      hasNext: () ->
        state.currentIndex + 1 < state.length

      hasPrev: () ->
        state.currentIndex > 0

      remaining: () ->
        if this.hasNext() then state.length - state.currentIndex - 1 else 0

      apply: (fns...) ->
        state.funcs = state.funcs.concat fns
        @

      get: (idx) ->
        [val] = @itemize idx
        state.currentIndex = idx
        if state.funcs.length
          fn = h.compose.apply null, state.funcs
          val = fn.call state.v, val, idx
        val

      next: () ->
        throw new Error('No more items') if not @hasNext()
        state.currentIndex += 1
        @get state.currentIndex

      prev: () ->
        throw new Error('No more items') if not @hasPrev()
        state.currentIndex -= 1
        @get state.currentIndex

      slice: (start=0, end, callback) ->
        if h.type start, 'function'
          callback = start
          start = 0
          end = null
        if h.type end, 'function'
          callback = end
          end = null
        lastIndex = @len() - 1
        if (not end?) or (end > lastIndex)
          end = lastIndex
        if end < 0
          end = lastIndex + end + 1
        if start < 0
          start = 0
        collected = []
        for i in [start..end]
          try
            item = @get i
            collected.push item
            callback(item) if h.type callback, 'function'
          catch e
            throw e if e isnt 'skip'
        collected

      each: (callback) ->
        for idx in state.indices
          callback.apply state.v, @itemize(idx)

      reduce: (callback, initial=0) ->
        for idx in state.indices
          initial = callback.apply state.v, [initial].concat @itemize idx
        initial

      every: (callback) ->
        for idx in state.indices
          return false if not callback.apply state.v, @itemize idx
        true

      none: (callback) ->
        for idx in state.indices
          return false if callback.apply state.v, @itemize idx
        true

      any: (callback) ->
        not @none(callback)

    # ### `#arrayIter(a)`
    #
    # Returns an [iterator object](#iterator-object) for the given array.
    #
    arrayIter: (a) ->
      state =
        v: [].concat a
        currentIndex: -1
        length: a.length
        indices: [0..a.length - 1]
        funcs: []

      h.create h.iterBase(state),
        itemize: (idx) ->
          [state.v[idx], idx]

        map: (callback) ->
          callback.apply(state.v, @itemize idx) for idx in state.indices

        filter: (callback) ->
          state.v[idx] for idx in state.indices when callback.apply state.v, @itemize idx


    # ### `#objIter(o)`
    #
    # Returns an [iterator object](#iterator-object) for the given object.
    #
    objIter: (o) ->
      keys = (k for k of o when Object::hasOwnProperty.call o, k)

      state =
        v: h.clone o
        indices: [0..keys.length - 1]
        currentIndex: -1
        length: keys.length
        funcs: []

      h.create h.iterBase(state),
        itemize: (idx) ->
          key = keys[idx]
          value = state.v[key]
          [value, key]

        indices: () ->
          keys

        get: (idx) ->
          val = this.__super__.get.call @, idx
          key = keys[idx]
          [key, val]

        map: (callback) ->
          o1 = {}
          for key, val of state.v
            o1[key] = callback.call state.v, val, key
          o1

        filter: (callback) ->
          o1 = {}
          for key, val of state.v
            o1[key] = val if callback.call state.v, val, key
          o1

    # ### `#iter(v)`
    #
    # Returns an [iterator object](#iterator-object) for arrays and objects. If
    # the argument is neither array nor object, it returns `undefined`.
    #
    iter: (v) ->
      switch h.type v
        when 'array' then h.arrayIter v
        when 'object' then h.objIter v
        else undefined

    # ### Iterator object
    #
    # Object returned from `#iter()`, `#objIter()` and `#arrayIter()`
    # functions. This object contains methods for working with sequences such
    # as arrays and objects.
    #
    # Objects are not strictly sequences. However, we can still apply all of
    # the functions of the iterator objects to plain objects as well by
    # treating their key-value pairs as sequence members. The main difference
    # is that we cannot (always) predict the order of the properties.
    #
    # #### `iterator.indices()`
    #
    # Retuns all array indices or object keys as an array.
    #
    # #### `iterator.len()`
    #
    # Returns the length of a sequence.
    #
    # #### `iterator.remaining()`
    #
    # Returns the number of remaining members that haven't been returned by
    # `iterator.next()`.
    #
    # #### `iterator.apply(fn, [fn...])`
    #
    # Adds one or more functions to be applied to each item returned from
    # `iterator.get()` and `iterator.next()` methods.
    #
    # There is one special exception that functions can throw, that is taken
    # into account when slicing sequences (see `iterator.slice()`). If the
    # function throws a simple string `'skip'` the member is simply omitted
    # from the slice without causing the exception to propagate further. Any
    # other exceptions are rethrown.
    #
    # #### `iterator.get(index)`
    #
    # Returns a member at the given index.
    #
    # `index` is an integer representing the member's index. This also applies
    # to objects as well, where the `index` is the index of the key in the
    # internal array of keys.
    #
    # #### `iterator.next()`
    #
    # Returns the next member of a sequence that comes after the member
    # returned in the previous call or a call to `iterator.get()`. When no next
    # memeber exist, it throws an exception. When none of the getter methods
    # have been called, it returns the first member.
    #
    # #### `iterator.prev()`
    #
    # Returns the previous member of a sequence that comes before the member
    # retruned in the previous call or a call to `iterator.get()`. When no
    # previous member exists, it throws an exception. When none of the getter
    # methods have been called or the current index of the iterator is 0, it
    # throws an exception.
    #
    # #### `iterator.slice([start, end, callback])`
    #
    # Returns a slice of the sequence starting with `start` index, and ending
    # with `end` index. Both indices are optional. If none is specified,
    # entire sequence is returned.
    #
    # If only the `end` index is omitted, the method returns the part of the
    # sequence starting with `start` index all the way to the last member.
    #
    # The `end` index can also be a negative integer, in which case it
    # represents the number of members from the last index towards the start.
    #
    # `start` index can be larger than the `end` index, in which case the
    # sequence is iterated backwards.
    #
    # An optional `callback` function can be passed that will be called for
    # each member of the slice.
    #
    # #### `iterator.each(callback)`
    #
    # Invokes a callback on each member of the sequence.
    #
    # The callback function is bound to the sequence itself, and has the
    # following signature:
    #
    #     callback(item, index)
    #
    #  + `item`: the member of the sequence.
    #  + `index`: the index or key of the member within the sequence.
    #
    # #### `iterator.map(callback)`
    #
    # Invokes a callback on each member of the sequence and returns a new
    # sequence that consists of callback's return values.
    #
    # The callback function is bound to the sequence itself, and has the
    # following signature:
    #
    #     callback(item, index)
    #
    #  + `item`: the member of the sequence.
    #  + `index`: the index or key of the member within the sequence.
    #
    # #### `iterator.reduce(callback, initial=0)`
    #
    # Reduces a sequence to a single value by invoking a callback on each
    # member.
    #
    # The callback function is bound to the sequence itself, and has the
    # following signature:
    #
    #     callback(value, item, index)
    #
    #  + `value`: current value in reduction (this is the `initial` value when
    #    reduction starts).
    #  + `item`: the member of the sequence.
    #  + `index`: the index or key of the member within the sequence.
    #
    # #### `iterator.every(callback)`
    #
    # Invokes a callback on each member of the sequence and returns `true` if
    # the callback returns `true` for each member.
    #
    # The callback function is bound to the sequence itself, and has the
    # following signature:
    #
    #     callback(item, index)
    #
    #  + `item`: the member of the sequence.
    #  + `index`: the index or key of the member within the sequence.
    #
    # #### `iterator.none(callback)`
    #
    # Invokes a callback on each member of the sequence and returns `true` if
    # the callback returns `false` for each member.
    #
    # The callback function is bound to the sequence itself, and has the
    # following signature:
    #
    #     callback(item, index)
    #
    #  + `item`: the member of the sequence.
    #  + `index`: the index or key of the member within the sequence.
    #
    # #### `iterator.any(callback)`
    #
    # Invokes a callback on each member of the sequence and returns `true` if
    # the callback returns `true` for at least one member. This is the opposite
    # of `iterator.none()`.
    #

    # ## Functional helpers
    #

    # ### `#lazy(fn)`
    #
    # Returns a function that returns a proxy object whose value will be the
    # result of calling the `fn` function when its `#valueOf` method is called.
    #
    # Because the `valueOf` method is used by JavaScript when values are being
    # coerced, this function works best with functions whose return values are
    # going to be used in a situation where coercion int primitive vlues is
    # possible.
    #
    # Example:
    #
    #     var fn = function (a, b) { return a + b; }
    #     fn = dahelpers.lazy(fn);
    #     var r = fn(1, 2); // original `fn` is not yet called at this point
    #     r + 2; // now the original `fn` is called, and result is 5
    #
    lazy: (fn) ->
      (args...) ->
        valueOf: () ->
          fn.apply null, args

    # ### `#compose([fn...])`
    #
    # Composes functions passed as arguments into a single function.
    #
    # Example:
    #
    #     var fn1 = function () { ... };
    #     var fn2 = function () { ... };
    #     var fn3 = function () { ... };
    #     var fn4 = dahelpers.compose(fn1, fn2, fn3);
    #     // `fn4(args...)` is same as fn1(fn2(fn3(args...))
    #
    compose: (funcs...) ->
      (args...) ->
        args == arguments
        for fn in funcs by -1
          args = [fn.apply null, args]
        args[0]

    # ### `#suicidal(fn)`
    #
    # Returns a version of the function that undefines itself (commits suicide)
    # after first call.
    #
    # Example:
    #
    #     var fn = function (x) { return x + 1; }
    #     fn = dahelpers.suicidal(fn);
    #     fn(2); // returns 3
    #     fn(4); // returns undefined
    #
    suicidal: (fn) ->
      () ->
        fn.apply null, arguments
        fn = () ->

    # ### `#throttled(fn, period, [bindTo])`
    #
    # Returns a throttled version of function that will execute at most once in
    # `period` when called repeatedly. The period is in milliseconds.
    #
    # Optional `bindTo` argument can point to an object to which the function
    # should be bound. Default is `null`.
    #
    # Example:
    #
    #      var throttled = dahelpers.throttled(function() {
    #          console.log('called');
    #      }, 1000);
    #      while (true) { throttled(); }
    #      // Only logs once every second (and eventually crashes)
    #
    throttled: (fn, period, bindTo=null) ->
      lastCall = null
      (args...) ->
        if not lastCall or Date.now() - lastCall >= period
          lastCall = Date.now()
          fn.apply bindTo, args

    # ### `#debounced(fn, period, [bindTo])`
    #
    # Returns a debounced version of function that will execute at most once
    # when `period` milliseconds had elapsed since last call.
    #
    # Optional `bindTo` argument can point to an object to which the function
    # should be bound. Default is `null`.
    #
    # Example:
    #
    #     var debounced = dahelpers.debounced(function() {
    #         console.log('called');
    #     }, 50);
    #     var numCalls = 20;
    #     var interval = setInterval(function() {
    #         debounced();
    #         numCalls -= 1;
    #         if (!numCalls) { clearInterval(interval); }
    #     }, 10);
    #     // Calls `debounced()` 20 times in 10ms intervals.
    #     // 'called' is logged only once, 50ms after the last call
    #
    debounced: (fn, period, bindTo=null) ->
      timeout = null
      (args...) ->
        clearTimeout timeout if timeout?
        timeout = setTimeout () ->
          fn.apply bindTo, args
        , period

    # ### `#queued(fn, [period, bindTo])`
    #
    # Adds functions calls to a queue and executes the queue all at once
    # `period` milliseconds after the last call. Period can be omitted, in
    # which case the queue is never executed automatically.
    #
    # The returned function has a method (yes, you read that right, a method)
    # `#run()` which can be called to force immediate execution of the queue
    # even if the timeout has not been reached. You can simply omit the
    # `period` argument as well and use this method exclusively.
    #
    # Optional `bindTo` argument can point to an object to which the function
    # should be bound. Default is `null`.
    #
    # Examples:
    #
    #     var counter = 0;
    #     var queued = dahelpers.queued(function() {
    #         counter += 1;
    #     }, 50);
    #     var numCalls = 20;
    #     var interval = setInterval(function() {
    #         queued();
    #         // Counter is still 0 here
    #         numCalls -= 1;
    #         if (!numCalls) { clearInterval(interval); }
    #     }, 10);
    #     // After 50ms after last call is made, counter is incremented by 1,
    #     // 20 times.
    #
    #     var accumulated = 0;
    #     var queued = dahelpers.queued(function(x) {
    #         accumulated += x;
    #     });
    #     var i = 5;
    #     for (; i; i -= 1) {
    #         queued(i);
    #     }
    #     // accumulated is still 0 at this point
    #     queued.run();
    #     // accumulated is now 15
    #
    queued: (fn, period=null, bindTo=null) ->
      queueArgs = []
      timeout = null

      if arguments.length is 2
        if not h.type period, 'number'
          bindTo = period
          period = null

      execQueue = () ->
        for a in queueArgs
          fn.apply bindTo, a

      queued = (args...) ->
        queueArgs.push args
        if period?
          clearTimeout timeout if timeout?
          timeout = setTimeout execQueue, period

      queued.run = () ->
        clearTimeout timeout
        execQueue()
        queueArgs = []

      queued

    # ## Formatting
    #

    # ### `#objAttrs(o)`
    #
    # Converts a JavaScript object `o` into a set of HTML attributes where a
    # key is the attribute name, and value is the attribute value.
    #
    # Note that the validity of attribute names are not checked, so it's
    # developer's job to make sure valid attributes are being generated.
    #
    # All attribute values are double-quoted and any double quotes inside the
    # attribute values are escaped.
    #
    # Example:
    #
    #     dahelpers.obAttrs({foo: 1, bar: 'foo'});
    #     // returns 'foo="1" bar="foo"'
    #
    objAttrs: (o) ->
      attrs = []
      for key of o
        val = o[key] or ''
        attrs.push "#{key}=\"#{val.replace(/"/g, '\\"')}\""
      attrs.join ' '

    # ### `#tag(name, content, [attrs, silence])`
    #
    # Wraps optional content into a HTML tag with optional attributes hash.
    #
    # The `name` represents the name of the HTML tag (and it is not checked for
    # validity at all. The `attrs` is an object whic is passed to
    # [`#objAttrs()`](#objattrs-o).
    #
    # If the `silence` argument is `true`, the whole `tag` is only rendered if
    # `content` is not null or undefined, and can be coerced into a non-empty
    # string.
    #
    # Example:
    #
    #     dahelpers.tag('a', 'click here', {href: '#'});
    #     // returns '<a href="#">click here</a>'
    #
    tag: (name, content='', attrs=null, silence=false) ->
      return '' if not name
      return '' if silence and (not content? or content.toString() is '')
      s = "<#{name}"
      s += " #{h.objAttrs(attrs)}" if attrs
      s += ">#{content}</#{name}>"
      s

    # ### `#escape(s)`
    #
    # Escapes special characters in string `s` as a measure for preventing XSS
    # attacks.
    #
    # Exampple:
    #
    #     dahelpers.escape('<a href="#">not so malicious HTML</a>')
    #     // returns:
    #     // '&lt;a href=&quot;#&quot;&gt;not so malicious HTML&lt;&#x2F;a&gt;'
    #
    escape: (s) ->
      return '' if not s?
      s = s.toString()
      for chr, esc of h.HTML_ESCAPE_MAPPINGS
        s = s.replace new RegExp(chr, 'g'), esc
      s

    # ### `#plural(singular, plural, [plural2...] count)`
    #
    # Provides support for pluralization. All but the last argument are plural
    # forms, starting with singular, which is the first argument, followed by 0
    # or more plural forms.
    #
    # The function will return an empty string if at least one form of singular
    # and one form of plural are not passed along with the count.
    #
    # The pluralization rules are actually defined in the
    # [`PLURAL_RULES`](#plural_rules) property, which is a function that
    # returns 0 for singular, and 1 or more for plural forms. The correct form
    # is then selected from the arguments passed to this function.
    #
    # Example:
    #
    #     dahelpers.plural('bear', 'bears', 3);  // returns 'bears'
    #
    plural: (args...) ->
      return '' if not args.length or args.length < 3
      count = args.pop()  # Last argument is count
      forms = args
      forms[h.PLURAL_RULES count]

    # ### `#capitalize(s)`
    #
    # Capitalizes the first character of the string `s`. You can used this to
    # build sentence case.
    #
    # Example:
    #
    #     dahelpers.capitalize('foo bar fam');  // returns 'Foo bar fam'
    #
    capitalize: (s) ->
      return '' if not s
      "#{s[0].toUpperCase()}#{s[1..]}"

    # ### `#titleCase(s, [lowerFirst])`
    #
    # Converts the string `s` to Title Case.
    #
    # This function uses a simple algorhythm for title-casing, so do not expect
    # exceptions (e.g., it cannot do fancy title cases such as 'Question of
    # Time').
    #
    # You can change the [`FIRST_CHAR`](#first_char) variable to customize the
    # regular expression used to find the first character if you need a more
    # complex behavior.
    #
    # To understand how the customization works here is a short description of
    # what `#titleCase()` does with the regexp internally.  The regexp is used
    # in a `String.prototype.replace()` call as the first argument, and the
    # callback function is passed the entire match. The match (not any captured
    # group) is then capitalized using [`#capitalize()`](#capitalize-s).
    #
    # Because of the way this function works, you generally must include the
    # 'g' flag in your regexp. The rest is up to you. There is a very crude
    # example of a customized title case which only capitalizes words that are
    # longer than 4 and contain only letters.
    #
    # If the `lowerFirst` is `ture`, the whole string will be lower-cased
    # before applying the title case. Default is `false`.
    #
    # Examples:
    #
    #     dahelpers.titleCase('This is a title');
    #     // returns 'This Is A Title'
    #
    #     dahelpers.FIRST_CHAR = /\b[a-z]{4,}/gi;
    #     dahelpers.titleCase('This is the title');
    #     // returns 'This is the Title'
    #
    titleCase: (s, lowerFirst=false) ->
      return '' if not s
      s = s.toLowerCase() if lowerFirst
      s.replace h.FIRST_CHAR, (match) ->
        h.capitalize match

    # ### `#format(s, format, [formatChar])`
    #
    # Formats a string according to the `format`. The format is simply a series
    # of hash character '#' that map the string's characters to appropriate
    # places one by one.
    #
    # This works best with source strings were internal structure has no
    # semantic like unformatted phone numbers or serial numbers. It doesn't
    # work well for strings that already have structure or whose length is
    # variable.
    #
    # The character used in the `format` string can be customed either by
    # passing an alternative as `formatChar` argument, or by modifying the
    # [`FORMAT_CHARACTER`](#format_character) variable.
    #
    # Examples:
    #
    #     dahelpers.format('abcdef', '##-##-##');  // returns 'ab-cd-ef'
    #     dahelpers.format('John Doe', '## ###');  // returns 'Jo hnD'
    #     dahelpers.format('1234', '$$$-$', '$');  // returns '123-4'
    #
    format: (s, format, formatChar=h.FORMAT_CHARACTER) ->
      return '' if not s
      s = '' + s # Coerce into string
      return s if not format
      s = s.split '' # Splits into individual characters as array
      for chr in s
        ## Replace first unreplaced '#' with `chr`
        format = format.replace(formatChar, chr)
      format

    # ### `#reverse(s)`
    #
    # Reverses a string.
    #
    # Example:
    #
    #     dahelpers.reverse('esrever');  // returns 'reverse'
    #
    reverse: (s) ->
      if s then s.split('').reverse().join '' else ''

    # ### `#sgroup(s, n)`
    #
    # Groups the string's characters into groups of `n` characters and returns
    # the groups as an array.
    #
    # The last group can be shorter than `n` if there are not enough
    # characters.
    #
    # An empty string is returned if `s` is not defined or is an empty string,
    # and an array containing the orginal string if `n` is not specified or is
    # 0.
    #
    # Examples:
    #
    #     dahelpers.sgroup('Groupings', 3);  // returns ['Gro', 'upi', 'ngs']
    #     dahelpers.sgroup('Grouping', 3);   // returns ['Gro', 'upi', 'ng']
    #
    sgroup: (s, n) ->
      return [] if not s? or s is ''
      s = s.toString()
      return [s] if not n
      m = s.match new RegExp "(.{1,#{n}})", 'g'
      m

    # ### `#pad(s, len, [char, tail, sep])`
    #
    # Pads a string `s` with `char` characters, so that the output is at least
    # `len` long.
    #
    # The `char` is '0' by default.
    #
    # If `len` is 0 or less than the length of `s`, no padding is done, and the
    # original string is left intact.
    #
    # Tail has the same meaning as `len` but from the tail end of the string.
    # The `sep` character is used to split the string into head and tail, and
    # they are padded separately and re-merged using the same separator
    # character. The `tail` of 0 will omit the part after the `sep` separator.
    # For numbers, this may be similar to coercing into integer without
    # rounding.
    #
    # The only case where `tail` behaves differently than `len` is when it is
    # set to `false`. This has a special meaning internally, where it disables
    # any processing of the tail if it is `false`.
    #
    # Examples:
    #
    #     dahelpers.pad('2', 2);             // returns '02'
    #     dahelpers.pad('2.5', 0, null, 3);  // returns '2.50'
    #
    pad: (s, len, char='0', tail=false, sep='.') ->
      if s? then s = s.toString() else return ''
      if tail is false
        if s.length < len
          ((new Array len).join(char) + s).slice -len
        else
          s
      else
        [s, t] = s.toString().split sep
        if tail is false
          h.pad s, len, char
        else
          ## Pad the head-end
          s = h.pad s, len, char

          ## Return just the head end if tail is 0
          return s if tail is 0

          ## Pad the tail end
          t or= char
          t = h.pad h.reverse(t), tail, char
          t = h.reverse(t)
          [s, t].join sep

    # ### `#thousands(num, [sep, decSep])`
    #
    # Adds the thousands separator to `num`.
    #
    # Default separator is a comma, and can be customized by passing the `sep`
    # argument.
    #
    # The `decSep` argument can be used to customize the decimal separator ('.'
    # by default).
    #
    # Although the `decSep` can control the output decimal separator, the input
    # decimal separator is always period. This is a tradeoff to give
    # `#thousands()` the ability to take JavaScript numbers as input, and still
    # use a different separator in the output without cluttering the function
    # signature.
    #
    # Examples:
    #
    #     dahelpers.thousands(1200000);               // returns '1,200,000'
    #     dahelpers.thousands(1200000.12, '.', ',');  // returns '1.200.000,00'
    #
    thousands: (num, sep=',', decSep='.') ->
      return '' if not num?
      num = num.toString()
      num = num.replace /[^\d\.-]/g, ''
      num = parseFloat(num)
      return '' if isNaN(num)
      [num, frac] = num.toString().split '.'
      num = h.reverse num
      num = h.sgroup(num, 3).join(sep)
      num = h.reverse num
      num = "#{num}#{decSep}#{frac}" if frac
      num

    # ### `#si(num, [d, thousands, sep, decSep])`
    #
    # Converts the number to closes SI factor (Kilo, Mega, etc). Uses only
    # factors of thousand (k, M, G, T, P, E, and Z) larger than 0.
    #
    # Due to overlow issues, the Y suffix is not avilable.
    #
    # The function will only add the next bigger suffix if the number is
    # divisible by that factor. For example, 1000 can use the 'k' suffix, but
    # 1100 will be returned as is.
    #
    # If `d` is specified, it will allow `d` number of decimals after the main
    # unit. For example, with number 1100, with `d` of 1, the function will add
    # return '1.1k'. With `d` of 1, 1110 would still be returned as is.
    # Increasing `d` to 2 would allow the function to output '1.11k'. And so on.
    # `d` can be as large as you want.
    #
    # if `thousands` is `true`, the thousands separator will be added.
    #
    # You can control the characters used for separator and decimal separator
    # by using the `sep` and `decSep` arguments. They work the same way as the
    # `thousands`.
    #
    # Examples:
    #
    #     dahelpers.si(1000);                 // returns '1k'
    #     dahelpers.si(1200);                 // returns '1200'
    #     dahelpers.si(1200, 1);              // returns '1.2k'
    #     dahelpers.si(1200, null, true);     // returns '1,200'
    #
    si: (num, d=0, thousands=false, sep=",", decSep='.') ->
      return '' if not num?
      units = 'kMGTPEZ'.split ''
      units.unshift ''

      ## Add `d` zeros to the number before starting
      adjustment = Math.pow(10, d)
      num = num * adjustment

      factor = 0
      for unit, idx in units
        if num % 1000
          num = num / adjustment
          if thousands
            num = h.thousands(num, sep, decSep)
          else
            num = num.toString().replace('.', decSep)
          return "#{num}#{unit}"
        else
          num = num / 1000

    # ### `#digits(s)`
    #
    # Removes all non-digit characters from a string. This includes decimal
    # points, minus sign, and anyting else that does not match the `\d` regular
    # expression.
    #
    # Examples:
    #
    #     dahelpers.digits('123.456.7890');           // returns '1234567890'
    #     dahelpers.digits('Number of items is 12');  // returns '12'
    #
    digits: (s) ->
      return '' if not s?
      s.toString().replace(/[^\d]/g, '')

    # ### `#prefix(num, prefix, sepLong)`
    #
    # Adds a prefix to a number. The `prefix` argument can be any string of any
    # length. `num` can be a real number, or just any string.
    #
    # The main difference between `#prefix()` and simple string concatenation
    # is the handling of the leading minus sign. If there is a minus sign at
    # the beginning of the number, the prefix will be inserted between the
    # minus sign and the rest of the number.
    #
    # The `sepLong` argument is used to separate long prefixes from the number.
    #
    # Examples:
    #
    #     dahlperss.prefix(12, '$');          // returns '$12'
    #     dahelpers.prefix(-12, '$');         // returns '-$12'
    #     dahelpers.prefix(12, 'foo');        // returns 'foo12'
    #     dahelpers.prefix(12, 'foo', true);  // returns 'foo 12'
    #
    prefix: (num, prefix, sepLong=false) ->
      return '' if not num?
      num = num.toString()
      return num if not prefix and not prefix.length

      if prefix.length > 1 and sepLong
        return "#{prefix} #{num}"

      if num[0] is '-'
        "-#{prefix}#{num[1..]}"
      else
        "#{prefix}#{num}"

    # ### `#round(num, [d])`
    #
    # Round the number to `d` decimal places. `d` is 0 by default.
    #
    # Examples:
    #
    #     dahelpers.round(12.34);     // returns 12
    #     dahelpers.round(12.34, 1);  // returns 12.3
    #
    round: (num, d=0) ->
      num = parseFloat num
      return 0 if isNaN num
      Math.round(num * Math.pow(10, d)) / Math.pow(10, d)

    # ### `#currency(num, [currency, dec, sep, decSep, si, suffix])`
    #
    # Formats `num` as currency  with thousands separator or SI suffix. Default
    # currency is '$', and thousands separators are used by default.
    #
    # The `dec` argument specifies the number of decimal places (default is 2).
    # This number is also used when converting to SI suffix. The value of 0
    # will completely omit the decimal places (this is not the same as
    # rounding, though).
    #
    # The `sep` argument specifies the thousands separator (default is ',').
    #
    # The `decSep` argument specifies the decimal separator (default is '.').
    #
    # The `si` argument should be a boolean and tells the function to render
    # the number with SI prefix instead of with thousands separator. Default is
    # `false`.
    #
    # The `suffix` argument is used to suffix the currency instead of prefixing
    # it.
    #
    # Example:
    #
    #     dahelpers.currency(12);            // returns '$12.00'
    #     dahelpers.currency(12, null, 0);   // returns '$12'
    #     dahelpers.currency(12, 'Fr');      // returns 'Fr 12.00'
    #     dahelpers.currency(12, 'USD');     // returns 'USD 12.00'
    #
    currency: (num, currency=h.DEFAULT_CURRENCY, dec=2, sep=',', decSep='.',
      si=false, suffix=false) ->
      if si
        num = h.si num, dec, true, sep, decSep
      else
        num = h.round num, dec
        num = h.thousands(num, sep, decSep)
        num = h.pad num, 0, '0', dec, decSep
      if suffix
        "#{num} #{currency}"
      else
        h.prefix num, currency, true

    # ### `#makeCurrency(name, currency, dec, sep, decSep, si, suffix)`
    #
    # Because the `#currency()` function takes many arguments and you might not
    # always use them all, this function will help you create a somewhat
    # permanent alias for the mix of arguments you wish to use often.
    #
    # Except for the `name` argument, the others are passed through to
    # [`#currency()`](#currency-num-currency-dec-sep-decsep-si-suffix)
    # function, and work the same way. The `name` is the name you wish to use
    # to refer to the currency. You can basically use any name you want, but
    # since the name is used to create a new key on JavaScript object, you
    # should use a name that can be used effectively in that context.
    #
    # The function returns a function which takes only the `num` argument and
    # uess previously specified arguments to return formatted currency. The
    # function is also accessible through `dahelpers._NAME` key where `NAME` is
    # the name you originally specified.
    #
    # To modify the definition of an existing currency, simply call this
    # function again and use the same name. To remove a currency, you should
    # simply `delete` the property from the `dahelpers` module (see examples
    # below).
    #
    # Examples:
    #
    #     dahelpers.makeCurrency('din', 'Din', 2, '.', ',', false, true);
    #     dahelpers._din(15000);  // returns '15.000,00 Din'
    #     delete dahelpers._din;  // removes 'din' currency
    #
    makeCurrency: (name, currency, dec, sep, decSep, si, suffix) ->
      h["_#{name}"] = (num) ->
        h.currency(num, currency, dec, sep, decSep, si, suffix)

    # ### `#siCurrency(num, [currency, dec, sep, decSep])`
    #
    # This is a shortcut for
    # [`#currency()`](#currency-num-currency-dec-sep-decsep-si-suffix) which
    # passes the si argument.
    #
    # Example:
    #
    #     dahelpers.siCurrency(1200, 'Fr');  // returns 'Fr 1.2k'
    #
    siCurrency: (num, currency, dec, sep, decSep, suffix) ->
      h.currency num, currency, dec, sep, decSep, true, suffix

    # ### `dollars(num, dec, si)`
    #
    # Shortcut function for formatting US currency.
    #
    # Example:
    #
    #     dahelpers.dollars(100);  // returns '$100.00'
    #
    dollars: (num, dec, si, suffix) ->
      h.currency num, h.USD, dec, null, null, si, suffix

    # ### `#euros(num, dec, si)`
    #
    # Shortcut function for formatting EU currency.
    #
    # Example:
    #
    #     dahelpers.euros(100);  // returns '€100.00'
    #
    euros: (num, dec, si, suffix) ->
      h.currency num, h.EUR, dec, null, null, si, suffix

    # ### `#yen(num, dec, si)`
    #
    # Shortcut function for formatting Japanese currency.
    #
    # Example:
    #
    #     dahelpers.yen(100);  // returns '¥100.00'
    #
    yen: (num, dec, si, suffix) ->
      h.currency num, h.YN, dec, null, null, si, suffix

    # ### `#yuan(num, dec, si)`
    #
    # Shortcut function for formatting Chinese currency. Since both Chinese and
    # Japanese currencies use the same symbol, this function is a simple alias
    # for [`#yen()`](#yen-num-dec-si).
    #
    # Example:
    #
    #     dahelpers.yuan(100);  // returns '¥100.00'
    #
    yuan: (args...) ->
      h.yen args...

    # ### `#pounds(num, dec, si)`
    #
    # Shortcut function for formatting UK currency.
    #
    # Example:
    #
    #     dahelpers.pounds(100); // returns '£100.00'
    #
    pounds: (num, dec, si, suffix) ->
      h.currency num, h.GBP, dec, null, null, si, suffix

    # ### `#wrap(s, [len, sep])`
    #
    # Wraps the text to make lines of `len` length separated by `sep`
    # separator. The `len` is 79 by default, and separator is a LF character
    # ('\n').
    #
    # Default wrap width can be customized globally by changing the
    # [`WRAP_WIDTH`](#wrap_width) variable.
    #
    # Code for this function is based on the idea from [James Padolsey's blog
    # post](http://james.padolsey.com/javascript/wordwrap-for-javascript/).
    #
    # Example:
    #
    #     dahelpers.wrap('The quick brown fox jumps over lazy old fox.', 20);
    #     // returns:
    #     // 'The quick brown\n
    #     // fox jumps over\n
    #     // lazy old fox.'
    #
    wrap: (s, len=h.WRAP_WIDTH, sep='\n') ->
      return '' if not s?
      rxp = new RegExp ".{1,#{len}}(\\s|$)", "g"
      lines = s.match(rxp)
      lines = (l.replace(/\s*$/, '') for l in lines)  # Strip trailing spaces
      lines.join(sep)

    # ### `#slug(s)`
    #
    # Converts a string to a slug (URL-compatible string). This function is
    # fairly basic, so don't depend on it for strings that contain non-ASCII
    # letters.
    #
    # Example:
    #
    #     dahelpers.slug('This is some text.');
    #     // returns 'this-is-some-text'
    #
    slug: (s) ->
      return '' if not s
      s = s.toString().toLowerCase().replace /\W+/g, '-'
      s = s.replace /[_-]+$/, ''  # Strip trailing non-letters
      s.replace /^[_-]+/, ''  # Strip leading non-letters

  # ### Tag aliases
  #
  # For convenience we include a few aliases for HTML tags that will call
  # `#tag()` function with a specific HTML tag name. The tags that are aliased
  # are:
  #
  #  + a
  #  + p
  #  + strong
  #  + em
  #  + ul
  #  + ol
  #  + li
  #  + div
  #  + span
  #  + button
  #  + option
  #
  # They take the same arguments as the `#tag()` function except `name`.
  #
  ((tags) ->
    for tag in tags
      h[tag] = ((t) ->
        (args...) ->
          args.unshift t
          h.tag.apply h, args
      ) tag
    return
  ) 'a p strong em ul ol li div span button option'.split ' '

  h # return the module

# ## Running tests
#
# To run the tests you first need to install all development dependencies. In
# the source directory run:
#
#     npm install
#
# Next run:
#
#     node node_modules/mocha/bin/_mocha tests/*.js
#
# To run tests in your browser, simply open `index.html` located in `tests`
# directory.
#
# ## Reporting bugs
#
# Please report all bugs to the [GitHub issue
# tracker](https://github.com/foxbunny/dahelpers/issues). Please check if there
# are any failing tests and include that information in the report.
#
