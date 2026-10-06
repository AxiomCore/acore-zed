; Types

(clazz (identifier) @type)
(typeAlias (identifier) @type)
((identifier) @type
 (#match? @type "^[A-Z]"))

(typeArgumentList
  "<" @punctuation.bracket
  ">" @punctuation.bracket)

; Method definitions

(classMethod (methodHeader (identifier)) @function)
(objectMethod (methodHeader (identifier)) @function)

; Identifiers

(classProperty (identifier) @property)
(objectProperty (identifier) @property)

(parameterList (typedIdentifier (identifier) @variable.parameter))
(objectBodyParameters (typedIdentifier (identifier) @variable.parameter))

(identifier) @variable

; Literals

(stringConstant) @string
(slStringLiteralExpr) @string
(mlStringLiteralExpr) @string

(escapeSequence) @string.escape

(intLiteralExpr) @number
(floatLiteralExpr) @number

(stringInterpolation
  "\\(" @punctuation.special
  ")" @punctuation.special) @embedded

(stringInterpolation
 "\\#(" @punctuation.special
 ")" @punctuation.special) @embedded

(stringInterpolation
  "\\##(" @punctuation.special
  ")" @punctuation.special) @embedded

(lineComment) @comment
(blockComment) @comment
(docComment) @comment
(shebangComment) @comment

; Operators

"??" @operator
"@"  @operator
"="  @operator
"<"  @operator
">"  @operator
"!"  @operator
"==" @operator
"!=" @operator
"<=" @operator
">=" @operator
"&&" @operator
"||" @operator
"+"  @operator
"-"  @operator
"**" @operator
"*"  @operator
"/"  @operator
"~/" @operator
"%"  @operator
"|>" @operator

"," @punctuation.delimiter
":" @punctuation.delimiter
"." @punctuation.delimiter
"?." @punctuation.delimiter

"(" @punctuation.bracket
")" @punctuation.bracket
"[" @punctuation.bracket
"]" @punctuation.bracket
"{" @punctuation.bracket
"}" @punctuation.bracket

; Keywords

"abstract" @keyword
"amends" @keyword
"as" @keyword
"class" @keyword
"else" @keyword
"extends" @keyword
"external" @keyword
(falseLiteralExpr) @constant
"for" @keyword
"function" @keyword
"hidden" @keyword
"if" @keyword
(importExpr "import" @function)
(importExpr "import*" @function)
"import" @keyword
"import*" @keyword
"in" @keyword
"is" @keyword
"let" @keyword
"local" @keyword
(moduleExpr "module" @type.builtin)
(thisType) @type.builtin
"module" @keyword
"new" @keyword
(nullLiteralExpr) @constant
"open" @keyword
"out" @keyword
(outerExpr) @variable.builtin
"read" @function
"read?" @function
"read*" @function
"super" @variable.builtin
(thisExpr) @variable.builtin
"throw" @function
"trace" @function
(trueLiteralExpr) @constant
"typealias" @keyword
"when" @keyword

; Acore additions
(domainDeclaration name: (qualifiedIdentifier) @type)
(domainFunction name: (identifier) @function)
(domainBinding name: (identifier) @property)
(namedArgument name: (identifier) @property)
(implicitMemberExpr (identifier) @property)
(objectLiteralEntry (identifier) @property)
(styleContent) @string
(unitLiteralExpr) @number
[
  "profile"
  "override"
  "extension"
  "export"
  "perform"
  "invoke"
  "extend"
  "model"
  "endpoint"
  "entity"
  "projection"
  "relationship"
  "invariant"
  "variant"
  "policy"
  "enum"
  "app"
  "page"
  "screen"
  "component"
  "theme"
  "token"
  "stylesheet"
  "database"
  "schema"
  "table"
  "unique"
  "foreignKey"
  "index"
  "check"
  "service"
  "permission"
  "guard"
  "operation"
  "serverPolicy"
  "interceptor"
  "failure"
  "serverCache"
  "outbound"
  "multipart"
  "streamPolicy"
  "event"
  "publisher"
  "consumer"
  "job"
  "schedule"
  "webhook"
  "resource"
  "form"
  "pure"
  "action"
  "fn"
  "state"
  "derived"
  "computed"
  "query"
  "mutation"
  "view"
  "effect"
  "watch"
  "batch"
  "handle"
  "require"
  "route"
  "use"
  "contract"
  "from"
  "audience"
  "styles"
  "also"
] @keyword
"=>" @operator

; Current database and application forms (syntax context, not reserved words).
[  "aggregate"
  "array"
  "async"
  "collation"
  "composite"
  "denied"
  "domain"
  "emit"
  "evolution"
  "field"
  "foreignServer"
  "foreignTable"
  "form_model"
  "go"
  "grant"
  "layout"
  "materializedView"
  "migration"
  "not_found"
  "optimistic"
  "options"
  "partition"
  "path"
  "procedure"
  "range"
  "redirect"
  "referenceData"
  "replace"
  "role"
  "rowSecurity"
  "rule"
  "sequence"
  "server"
  "session"
  "signed_out"
  "store"
  "trigger"
  "update"
  "userMapping"] @keyword
(namedRouteDeclaration name: (identifier) @type)
(routeParameter name: (identifier) @variable.parameter)
(migrationDeclaration version: (intLiteralExpr) @number)
(workflowStatement command: (qualifiedIdentifier) @function)
((domainCall (qualifiedIdentifier) @keyword) (#match? @keyword "^(Exponential|Field|Fixed|Linear|adoptName|auth|backend|backfill|body|cache|cacheIdentity|cast|concurrently|convert|cors|defaultPrivileges|defaults|errors|eventTrigger|frontend|group|header|idempotency|intercept|invalidates|manage|managed|membership|mock|native|observability|offlineConfig|partitioning|policies|primaryKey|project|rateLimit|record|rename|request|response|responseCookie|responseHeader|result|retry|return_to|rowPolicy|sandbox|security|securityEvidence|serverDefaults|serverTelemetry|session_actions|stream|streaming|tableStorage|testConfig)$"))

; Nested catalog calls retain contextual colors when semantic tokens are off.
((unqualifiedAccessExpr (identifier) @keyword (argumentList)) (#match? @keyword "^(Exponential|Field|Fixed|Linear|adoptName|auth|backend|backfill|body|cache|cacheIdentity|cast|concurrently|convert|cors|defaultPrivileges|defaults|errors|eventTrigger|frontend|group|header|idempotency|intercept|invalidates|manage|managed|membership|mock|native|observability|offlineConfig|partitioning|policies|primaryKey|project|rateLimit|record|rename|request|response|responseCookie|responseHeader|result|retry|return_to|rowPolicy|sandbox|security|securityEvidence|serverDefaults|serverTelemetry|session_actions|stream|streaming|tableStorage|testConfig)$"))
((constructorExpr (qualifiedIdentifier) @keyword) (#match? @keyword "^(Exponential|Field|Fixed|Linear|adoptName|auth|backend|backfill|body|cache|cacheIdentity|cast|concurrently|convert|cors|defaultPrivileges|defaults|errors|eventTrigger|frontend|group|header|idempotency|intercept|invalidates|manage|managed|membership|mock|native|observability|offlineConfig|partitioning|policies|primaryKey|project|rateLimit|record|rename|request|response|responseCookie|responseHeader|result|retry|return_to|rowPolicy|sandbox|security|securityEvidence|serverDefaults|serverTelemetry|session_actions|stream|streaming|tableStorage|testConfig)$"))
((constrainedType (declaredType (qualifiedIdentifier) @keyword)) (#match? @keyword "^(Exponential|Field|Fixed|Linear|adoptName|auth|backend|backfill|body|cache|cacheIdentity|cast|concurrently|convert|cors|defaultPrivileges|defaults|errors|eventTrigger|frontend|group|header|idempotency|intercept|invalidates|manage|managed|membership|mock|native|observability|offlineConfig|partitioning|policies|primaryKey|project|rateLimit|record|rename|request|response|responseCookie|responseHeader|result|retry|return_to|rowPolicy|sandbox|security|securityEvidence|serverDefaults|serverTelemetry|session_actions|stream|streaming|tableStorage|testConfig)$"))
