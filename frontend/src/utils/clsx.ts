/**
 * Tiny utility to join class names conditionally.
 * Avoids the need for an external `clsx` or `classnames` package.
 */
export function clsx(...args: Array<string | undefined | null | false | 0>): string {
  return args.filter(Boolean).join(' ');
}
