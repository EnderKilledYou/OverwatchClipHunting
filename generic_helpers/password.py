import random
import string


def GenerateRandomWindowsPassword(password_length=35):
  """Generates a password that meets Windows complexity requirements."""
  # The special characters have to be recognized by the Azure CLI as
  # special characters. This greatly limits the set of characters
  # that we can safely use. See
  # https://github.com/Azure/azure-xplat-cli/blob/master/lib/commands/arm/vm/vmOsProfile._js#L145
  special_chars = '*!@#$%+='
  # Ensure that the password contains at least one of each 4 required
  # character types starting with letters to avoid starting with chars which
  # are problematic on the command line e.g. @.
  prefix = [random.choice(string.ascii_lowercase),
            random.choice(string.ascii_uppercase),
            random.choice(string.digits),
            random.choice(special_chars)]
  password = [
      random.choice(string.ascii_letters + string.digits + special_chars)
      for _ in range(password_length - 4)]
  return ''.join(prefix + password)
