from flask import session, render_template, Blueprint


route_error = Blueprint(__name__, "error")

# ErrorHandler
@route_error.errorhandler(404)
def error_404_notfound(error):
    return render_template("404.html",
                           session=session["user_id"])


