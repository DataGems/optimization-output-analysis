library(readr)
library(janitor)
library(tidyverse)
library(patchwork)
library(jsonlite)

jy_c102 <- read_csv("jy_c102.csv")

parse_custom_json <- function(json_text) {
  json_text_fixed <- gsub("NaN", "null", json_text)
  fromJSON(json_text_fixed)
}

json_file <- "yuck.json"
json_text <- readLines(json_file, warn = FALSE)
json_text <- paste(json_text, collapse = "")
data <- parse_custom_json(json_text)

df <- test

iter_data <- function(df){
  iterations <- length(df[["lblp_lower"]])
  results_df <- tibble(iteration = 1:iterations)
  
  simple_arrays <- c("lblp_lower", "did_compress", "lp_time_compress", 
                     "lp_time_LB", "lp_value_compress", 
                     "sum_lp_value_project", "sum_lp_time_project")
  
  for (array_name in simple_arrays) {
    if (array_name %in% names(df) && length(df[[array_name]]) == iterations) {
      results_df[[array_name]] <- df[[array_name]]
    }
  }
  
  prob_sizes <- df[["prob_sizes_at_start"]] |> as_tibble() |> 
    rename(prob_size_time=timeGraph,
           prob_size_cap=capGraph,
           prob_size_ng=ngGraph)
  results_df <- results_df |> add_column(prob_sizes)
  
  lp_time <- df[["lp_time_project"]] |> as_tibble() |> 
    rename(lp_time_time=timeGraph,
           lp_time_cap=capGraph,
           lp_time_ng=ngGraph)
  results_df <- results_df |> add_column(lp_time)
  
  lp_value <- df[["lp_value_project"]] |> as_tibble() 
  results_df <- results_df |> add_column(lp_value)
  
  results_df
}

df <- iter_data(data)


#write_csv(results_df, "optimization_iterations.csv")

lb_graph <- df |> ggplot(aes(x = iteration, y = lblp_lower)) +
  geom_line(color = "blue") +
  geom_point() +
  theme_minimal() +
  labs(
    title = "Lower Bound Progress Across Iterations",
    x = "Iteration",
    y = "Lower Bound (lblp_lower)"
  )

size_graph <- df |> select(iteration, prob_size_time, prob_size_cap) |>
  rename(Time=prob_size_time, Capacity=prob_size_cap) |> 
  pivot_longer(cols = c(Time, Capacity), names_to = "type", values_to = "value") |>
  ggplot(aes(x = iteration, y = value, color=type)) +
  geom_line() +
  theme_minimal() +
  theme(legend.title=element_blank()) +
  labs(
    title = "Problem Size Across Iterations",
    x = "Iteration",
    y = "Problem Size",
    caption = "Data from Discretization Discovery Algorithm"
  )

lb_graph + size_graph + plot_layout(ncol=1)

#####################

final_cap_graph <- data[["final_graph_node_2_agg_node"]][["capGraph"]] |> 
  stack() |> 
  mutate(
    node = as.numeric(str_sub(values,14,-2)),
    node = factor(node)
  ) |> 
  select(node,ind) |> 
  mutate(
    ind = as.character(ind)|> str_replace_all("\\(",""),
    ind = as.character(ind)|> str_replace_all("\\)","")
  ) |> 
  separate_wider_delim(ind, delim = ",", names = c("customer", "startCap", "endCap")) |> 
  mutate(
    customer = as.numeric(customer),
    startCap = as.numeric(startCap),
    endCap = as.numeric(endCap)
  )

final_time_graph <- data[["final_graph_node_2_agg_node"]][["timeGraph"]] |> 
  stack() |> 
  mutate(
    node = as.numeric(str_sub(values,15,-2)),
    node = factor(node)
  ) |> 
  select(node,ind) |> 
  mutate(
    ind = as.character(ind)|> str_replace_all("\\(",""),
    ind = as.character(ind)|> str_replace_all("\\)","")
  ) |> 
  separate_wider_delim(ind, delim = ",", names = c("customer", "startTime", "endTime")) |> 
  mutate(
    customer = as.numeric(customer),
    startTime = as.numeric(startTime),
    endTime = as.integer(endTime)
  ) |> 
  arrange(node,customer,startTime)

grouped_time_graph <- final_time_graph |> 
  group_by(node,customer) |> 
  summarise(
    startTime = min(startTime),
    endTime = max(endTime)
  ) |> 
  arrange(node,customer,startTime)

customer_time_graph <- grouped_time_graph |> arrange(customer,startTime)

location_time_graph <- grouped_time_graph |> left_join(jy_c102, by="customer") |> 
  mutate(in_window = startTime >= due_date & endTime <= ready_time)

location_time_graph |> tabyl(node, in_window)

location_time_graph |> ggplot(aes(x=xcoord,y=ycoord,color=node,shape = node, size=3)) +
  scale_shape_manual(values=1:nlevels(location_time_graph$node)) +
  geom_point()

final_time_graph |> tabyl(node)


customer_time_graph  |> 
  left_join(windows) |> 
  ggplot(
    aes(
      x = startTime,
      xend = endTime,
      y = customer,
      color = node
    )
  ) +
  geom_dumbbell(
    #    colour = "#a3c4dc",
    #    colour_xend = "#0e668b",
    size = 2
  ) +
  geom_point(aes(x=due_date,y=customer))

windows <- jy_c102 |> select(customer,ready_time,due_date)



#location_time_graph |> write_csv("location_time_graph.csv")

ilp_solution <- data[["output_ilp_solution"]] |> stack() 

ilp_deltas <- ilp_solution |> filter(str_detect(ind,"delta")) |> 
  separate_wider_delim(ind, delim = "_", names = c("delta", "type", "customer")) |> 
  select(customer,type,values) |> 
  mutate(customer=factor(customer))
  
ilp_actions <- ilp_solution |> filter(str_starts(ind,"act")) |> 
  separate_wider_delim(ind, delim = "_", names = c("act", "fromNode", "toNode")) |> 
  select(fromNode,toNode,values) |> 
  filter(values==1) |> 
  mutate(
    fromNode = as.integer(fromNode),
    toNode = as.integer(toNode)
  )

ilp_prim_actions <- ilp_solution |> filter(str_starts(ind,"prim")) |> 
  separate_wider_delim(ind, delim = "_", names = c("prim", "act", "fromNode", "toNode")) |> 
  select(fromNode,toNode,values) |> 
  filter(values==1) |> 
  mutate(
    fromNode = as.integer(fromNode),
    toNode = as.integer(toNode)
  )


final_time_graph |> arrange(customer,node,startTime) |> View()

#########################  

create_routes <- function(df) {
  
  routes <- df |> filter(fromNode==25) |> 
    select(-values) |> 
    mutate(
      route=row_number(),
      stop = 1,
      unvisited=TRUE)
  
  while(TRUE){
    this_round <- routes |> filter(unvisited)
    if (nrow(this_round)==0) {
      break
    }
    
    to_add <- routes[0,]
    for (i in 1:nrow(this_round)) {
      cur_node = this_round$toNode[i]
      to_add <- to_add |> add_row(
        fromNode = cur_node,
        toNode = ilp_actions$toNode[ilp_actions$fromNode==cur_node],
        route = this_round$route[i],
        stop = this_round$stop[i] + 1,
        unvisited = ifelse(toNode==26, FALSE, TRUE)
      )
    }
    
    routes$unvisited <- FALSE
    routes <- routes |> bind_rows(to_add)
    
  }
  
  routes |> select(-unvisited) |> 
    arrange(route,stop)
  
}
  

tryit <- create_routes(ilp_actions)


tryit |> left_join(jy_c102, by=c("toNode" = "customer")) |> 
  write_csv("yuck_solution.csv")

#######################################

parse_custom_json <- function(json_text) {
  json_text_fixed <- gsub("NaN", "null", json_text)
  fromJSON(json_text_fixed)
}

read_one_file <- function(fname) {
  json_file <- fname
  json_file |> readLines(warn = FALSE) |> 
    paste(collapse = "") |> 
    parse_custom_json()
}



test <- read_one_file("output_no_ilp_50_time_window_10_empty_init/out_jy_r104.txt")

all_experiments$iter_data[8] |> hoist(1)

mytib$prob_size_time[nrow(mytib)]
nrow(mytib)

all_experiments |> mutate(
  newcol=iter_data[[1]]$prob_size_time[nrow(iter_data)]
)

length(test[["lblp_lower"]])

all_experiments[[10]][[5]] |> write_csv("sample_graph.csv")
