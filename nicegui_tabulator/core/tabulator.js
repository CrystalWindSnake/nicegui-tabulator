import { loadResource } from "../../static/utils/resources.js";
import { convertDynamicProperties } from "../../static/utils/dynamic_properties.js";
import 'tabulator'

const completedEvents = new Set([
  'tableBuilding',
  'tableBuilt',
]);

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

function onSocketConnect(fn) {
  window.Vue.nextTick(() => {
    const socket = window.socket;
    socket.on("connect", fn);
  });
}

export default {
  template: `<div></div>`,
  props: {
    options: Object,
    resource_path: String,
  },
  async mounted() {
    await new Promise((resolve) => setTimeout(resolve, 0)); // NOTE: wait for window.path_prefix to be set
    const hasNiceGuiTabulatorTheme = document.querySelector('link.nicegui-tabulator-theme') !== null;
    if (!hasNiceGuiTabulatorTheme) {
      await Promise.all([
        loadResource(window.path_prefix + `${this.resource_path}/tabulator.min.css`),
      ]);
    }

    convertDynamicProperties(this.options, true);
    this.table = new Tabulator(this.$el, this.options);

    this.table.on('tableBuilt', () => {
      setTimeout(() => {
        this.table.redraw();
      }, 800);
    });

    // here we need to wait for socket connection before emitting events, because some events may not be triggered at page load
    onSocketConnect(() => {
      this.$emit('connected');
    })

    this.$emit('connected');

  },

  methods: {
    onEvent(eventName) {
      const orgEventName = eventName.replace(/^table:/, '');

      // These events have already been completed at this moment
      if (completedEvents.has(orgEventName)) {
        this.$emit(eventName);
        return;
      }

      this.table.on(orgEventName, (...args) => {
        const eventArgs = extractEventArg(eventName, args);
        this.$emit(eventName, eventArgs);

        if (eventName === 'rowContext' || eventName === 'groupContext') {
          args[0].preventDefault();
        }
      });
    },
    run_table_method(name, ...args) {
      if (name.startsWith(":")) {
        name = name.slice(1);
        args = args.map((arg) => new Function(`return (${arg})`)());
      }
      return runMethod(this.table, name, args);
    },

    setColumns(columns) {
      convertDynamicProperties(columns, true);
      this.table.setColumns(columns);
    },

    updateColumnDefinition(field, definition) {
      convertDynamicProperties(definition, true);
      this.table.updateColumnDefinition(field, definition);
    },

    updateCellSlot(field, rowNumber, rowIndex) {
      this.$emit('updateCellSlot', { field, rowNumber, rowIndex })
    },

    resetRowFormat(position) {
      this.table.getRowFromPosition(position).normalizeHeight();
    }
  },
};