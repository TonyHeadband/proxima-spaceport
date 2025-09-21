export function validateNewRepo({ name, url, branch }) {
  const errors = []

  if (!name || name.trim().length < 3) {
    errors.push('Name must be at least 3 characters')
  }

  // Basic git url validation (http(s) or ssh) - simple regex
  const gitUrlPattern = /^(https?:\/\/|git@)[\w@:\/.\-~]+(\.git)?$/i
  if (!url || !gitUrlPattern.test(url.trim())) {
    errors.push('URL must be a valid git URL (https://... or git@...)')
  }

  if (!branch || branch.trim().length === 0) {
    errors.push('Branch must be provided')
  }

  return {
    ok: errors.length === 0,
    errors,
  }
}
