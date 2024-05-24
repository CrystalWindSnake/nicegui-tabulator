export default {
  template: `<Teleport :to="to"><slot></slot></Teleport>`,
  props: {
    to: String,
  },
};