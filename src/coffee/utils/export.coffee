((window) ->

  # Defines a global `o` object to serve as namespace
  window.o ?= {}

  # Releases the original `o` object and returns the current value of `o`
  window.releaseO = () ->
    mine = window.o
    window.o = window.oOrig
    mine

  # Exports a name to global `o` object within specified namespace
  window.export = (name, sub, obj) ->
    namespace = window.o[sub] ?= {}
    if namespace[name]?
      console.error "Name #{sub}.#{name} already defined with value #{window.o[name]}"
    namespace[name] = obj

) this
