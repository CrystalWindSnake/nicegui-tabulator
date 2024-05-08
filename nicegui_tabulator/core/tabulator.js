import { loadResource } from "../../static/utils/resources.js";


const eventArgsExtractor = new Map([
  ['dataFiltering', filters => ({ filters })],
  ['dataFiltered', (filters, rows) => ({ filters, rows: rows.map(row => row.getData()) })],

  ['dataSorting', sorters => ({ sorters })],
  ['dataSorted', (sorters, rows) => ({ sorters, rows: rows.map(row => row.getData()) })],

  ['pageLoaded', pageno => ({ pageno })],
  ['pageSizeChanged', pagesize => ({ pagesize })],
])


function extractEventArg(eventName, argsObject) {
  const result = {};

  if (eventArgsExtractor.has(eventName)) {
    return eventArgsExtractor.get(eventName)(...argsObject);
  }


  Object.keys(argsObject).forEach(key => {
    const obj = argsObject[key];
    if (obj.constructor.name === 'm') {
      // row
      result['row'] = obj.getData();
    } else if (obj.constructor.name === 'i') {
      // column
      result['column'] = obj.getDefinition();
    } else if (obj.constructor.name === 'o') {
      // cell
      result['cell'] = {
        row: obj.getData(),
        column: obj.getColumn().getDefinition(),
        value: obj.getValue(),
        oldValue: obj.getOldValue(),
      };
    }


  });

  return result;
}

export default {
  template: `<div></div>`,
  props: {
    options: Object,
    resource_path: String,
  },
  async mounted() {
    await this.$nextTick(); // NOTE: wait for window.path_prefix to be set
    await Promise.all([
      loadResource(window.path_prefix + `${this.resource_path}/tabulator.min.css`),
    ]);


    this.table = new Tabulator(this.$el, this.options);

  },

  methods: {
    onEvent(eventName) {

      this.table.on(eventName, (...args) => {
        const eventArgs = extractEventArg(eventName, args);
        this.$emit('table-event', { eventName, args: eventArgs });
      });
    },
    run_table_method(name, ...args) {
      if (name.startsWith(":")) {
        name = name.slice(1);
        args = args.map((arg) => new Function(`return (${arg})`)());
      }
      return runMethod(this.table, name, args);
    },
  },
};