import cpp

from FunctionCall fc
where
  fc.getTarget().hasName("memset")
select fc,"memset"