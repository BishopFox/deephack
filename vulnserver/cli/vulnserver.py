''' a skeleton cli program to begin development with '''
import os

from vulnserver.lib.vroutes import app

def main():
    ''' entry point for console_scripts, and cli binary '''
    app.run(host='0.0.0.0')
    # webscale database reloading
    os.system('''psql -d deephack -U deephack -c "drop owned by deephack"''')
    return 0

if __name__ == '__main__':
    main()
