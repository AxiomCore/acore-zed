(moduleClause (qualifiedIdentifier) @name) @item
(clazz "class" @context (identifier) @name) @item
(typeAlias "typealias" @context (identifier) @name) @item
(classMethod (methodHeader (identifier) @name)) @item
(classProperty (identifier) @name) @item
(objectProperty (identifier) @name) @item
(domainDeclaration name: (qualifiedIdentifier) @name) @item
(domainFunction name: (identifier) @name) @item
(domainBinding name: (identifier) @name) @item
(docComment) @annotation

(namedRouteDeclaration name: (identifier) @name) @item
(routeParameter name: (identifier) @name) @item
(migrationDeclaration version: (intLiteralExpr) @name) @item
(constructorExpr (qualifiedIdentifier) @name) @item
