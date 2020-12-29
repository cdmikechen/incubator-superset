/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import React from 'react';
import { hot } from 'react-hot-loader/root';
import thunk from 'redux-thunk';
import { createStore, applyMiddleware, compose, combineReducers } from 'redux';
import { Provider } from 'react-redux';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import { QueryParamProvider } from 'use-query-params';
import { initFeatureFlags } from 'src/featureFlags';
import { supersetTheme, ThemeProvider } from '@superset-ui/core';
import ErrorBoundary from 'src/components/ErrorBoundary';
import Menu from 'src/components/Menu/Menu';
import FlashProvider from 'src/components/FlashProvider';
import DashboardList from 'src/views/CRUD/dashboard/DashboardList';
import ChartList from 'src/views/CRUD/chart/ChartList';
import DatasetList from 'src/views/CRUD/data/dataset/DatasetList';
import DatabaseList from 'src/views/CRUD/data/database/DatabaseList';
import SavedQueryList from 'src/views/CRUD/data/savedquery/SavedQueryList';

import messageToastReducer from '../messageToasts/reducers';
import { initEnhancer } from '../reduxUtils';
import setupApp from '../setup/setupApp';
import setupPlugins from '../setup/setupPlugins';
import Welcome from './CRUD/welcome/Welcome';
import ToastPresenter from '../messageToasts/containers/ToastPresenter';

setupApp();
setupPlugins();

const container = document.getElementById('app');
const bootstrap = JSON.parse(container?.getAttribute('data-bootstrap') ?? '{}');
const user = { ...bootstrap.user };
const menu = { ...bootstrap.common.menu_data };
const common = { ...bootstrap.common };
initFeatureFlags(bootstrap.common.feature_flags);

export const superset_url_prefix: string = common.conf.SUPERSET_URL_PREFIX

const store = createStore(
  combineReducers({
    messageToasts: messageToastReducer,
  }),
  {},
  compose(applyMiddleware(thunk), initEnhancer(false)),
);

const App = () => (
  <Provider store={store}>
    <ThemeProvider theme={supersetTheme}>
      <FlashProvider common={common}>
        <Router>
          <QueryParamProvider ReactRouterRoute={Route}>
            <Menu data={menu} />
            <Switch>
              <Route path={superset_url_prefix + "/welcome/"}>
                <ErrorBoundary>
                  <Welcome user={user} />
                </ErrorBoundary>
              </Route>
              <Route path={superset_url_prefix + "/dashboards/list/"}>
                <ErrorBoundary>
                  <DashboardList user={user} />
                </ErrorBoundary>
              </Route>
              <Route path={superset_url_prefix + "/charts/list/"}>
                <ErrorBoundary>
                  <ChartList user={user} />
                </ErrorBoundary>
              </Route>
              <Route path={superset_url_prefix + "/tablemodelviews/list/"}>
                <ErrorBoundary>
                  <DatasetList user={user} />
                </ErrorBoundary>
              </Route>
              <Route path={superset_url_prefix + "/databaseviews/list/"}>
                <ErrorBoundary>
                  <DatabaseList user={user} />
                </ErrorBoundary>
              </Route>
              <Route path={superset_url_prefix + "/savedqueryviews/list/"}>
                <ErrorBoundary>
                  <SavedQueryList user={user} />
                </ErrorBoundary>
              </Route>
            </Switch>
            <ToastPresenter />
          </QueryParamProvider>
        </Router>
      </FlashProvider>
    </ThemeProvider>
  </Provider>
);

export default hot(App);
