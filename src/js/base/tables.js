import Tablesort from 'tablesort';

function initSortabletable(table) {
    new Tablesort(table);
}

export function initTables() {
    document.querySelectorAll('table').forEach(initSortabletable);
}
