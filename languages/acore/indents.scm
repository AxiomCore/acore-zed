[(objectBody) (classBody) (objectLiteralExpr) (listExpr) (styleBody) (mlStringLiteralExpr)] @indent
(_ "{" "}" @end) @indent
(_ "(" ")" @end) @indent
(_ "[" "]" @end) @indent
["}" "]" ")" "else"] @outdent
