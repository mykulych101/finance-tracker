export function renderSnakeCase(str: string) {
    return str
        .replace(/_/g, ' ')
        .split(' ')
        .map((word) => {
            return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        })
        .join(' ')
}
