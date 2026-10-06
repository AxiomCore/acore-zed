(clazz (classBody) @class.inside) @class.around
(domainDeclaration (objectBody) @class.inside) @class.around
(domainFunction (objectBody) @function.inside) @function.around
(classMethod) @function.around
(lineComment) @comment.around
(blockComment) @comment.around
