from static.ast import Node

@Node("StatementExpression", "in")
class StatementExpressionin:
    @classmethod
    def call(cls, r, self):
        r["active_graph"] = False
        return r

@Node("StatementExpression", "post-in")
class StatementExpressionout:
    @classmethod
    def call(cls, r, self):
        r["active_graph"] = True
        return r

@Node("Cast", "in")
class CastIn:
    @classmethod
    def call(cls, r, self):
        r["active_graph"] = False
        return r

@Node("Cast", "post-in")
class CastOut:
    @classmethod
    def call(cls, r, self):
        r["active_graph"] = True
        return r

