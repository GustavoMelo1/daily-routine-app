"""Initialize or migrate without dropping existing data."""
if __package__:
    from .migrate import main
else:
    from migrate import main

if __name__ == "__main__":
    main()
